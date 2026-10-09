"""Phase 2 evaluation: fine-tuned model vs frozen-feature baseline, plus the
"ID 900+" source probe.

Both models are trained on the same inner-train split of every outer fold, and
both get a per-head decision rule (src/eval/thresholds.py) learned on that
fold's inner-val split only. Evaluation-fold images never influence training,
model selection or thresholds. Every metric gets a group-bootstrap 95% CI, and
every main result is reported on all images and excluding IDs 900+.

Usage: python scripts/phase2_eval.py [--config configs/phase2_convnext_tiny.yaml]
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.dataset import load_images  # noqa: E402
from src.data.labels import CRITICAL_CLASS, HEAD_NAMES, HEADS, encode_labels, label_matrix  # noqa: E402
from src.eval.baseline import fit_lr_select_C, frozen_features, oof_logreg  # noqa: E402
from src.eval.metrics import cluster_bootstrap, paired_diff_ci, per_class_table, softmax  # noqa: E402
from src.eval.thresholds import adjusted_pred, class_prior, fit_alpha  # noqa: E402
from src.models.multitask import MultiTaskNet  # noqa: E402
from src.train.loop import predict  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402

SUBSETS = {"excl_900plus": lambda lab: lab.source_900plus.to_numpy() == 0,
           "all": lambda lab: np.ones(len(lab), bool)}
MODELS = {"finetuned": "fine-tuned", "baseline": "frozen + logreg"}
DECISIONS = ("tuned", "argmax")


def ft_probs(lg, tag_rows, names_idx, h):
    cols = [c for c in lg.columns if c.startswith(f"{h}_logit")]
    sub = tag_rows.set_index("image_name").loc[names_idx, cols]
    return softmax(sub.to_numpy())


def build_predictions(cfg, lab, Y, G, names, inner, lg, X, seed):
    """For each model and protocol: raw probabilities on eval images, argmax and
    tuned decisions, and the learned alphas."""
    idx_of = {n: i for i, n in enumerate(names)}
    out = {m: {p: {"P": {h: np.full((len(names), len(HEADS[h]["classes"])), np.nan) for h in HEAD_NAMES},
                   "pred_tuned": {h: np.full(len(names), -1) for h in HEAD_NAMES},
                   "pred_argmax": {h: np.full(len(names), -1) for h in HEAD_NAMES}}
               for p in ("cv", "secondary")} for m in MODELS}
    alphas = {m: {} for m in MODELS}
    for tag, sp in inner.items():
        proto = "cv" if tag.startswith("cv") else "secondary"
        tr, va, ev = (np.array([idx_of[n] for n in sp[r]]) for r in ("train", "val", "eval"))
        fold_id = int(tag[2:]) if proto == "cv" else -1
        rows = lg[(lg.protocol == proto) & (lg.fold == fold_id)]
        for k, h in enumerate(HEAD_NAMES):
            ncls = len(HEADS[h]["classes"])
            prior = class_prior(Y[tr, k], ncls)
            yv = Y[va, k]
            lv = yv >= 0
            # fine-tuned: logits saved by phase2_train for inner-val and eval
            pv_ft = ft_probs(lg, rows[rows.role == "inner_val"], names[va], h)
            pe_ft = ft_probs(lg, rows[rows.role == "eval"], names[ev], h)
            # baseline: logistic regression fit on the same inner-train split
            trl = tr[Y[tr, k] >= 0]
            m, C = fit_lr_select_C(X[trl], Y[trl, k], G[trl], cfg["baseline"]["C_grid"], seed)
            pv_bl = np.zeros((len(va), ncls))
            pe_bl = np.zeros((len(ev), ncls))
            pv_bl[:, m.classes_] = m.predict_proba(X[va])
            pe_bl[:, m.classes_] = m.predict_proba(X[ev])
            for mname, pv, pe in (("finetuned", pv_ft, pe_ft), ("baseline", pv_bl, pe_bl)):
                a, f1v = fit_alpha(yv[lv], pv[lv], prior)
                o = out[mname][proto]
                o["P"][h][ev] = pe
                o["pred_argmax"][h][ev] = pe.argmax(1)
                o["pred_tuned"][h][ev] = adjusted_pred(pe, prior, a)
                alphas[mname].setdefault(tag, {})[h] = {"alpha": a, "inner_val_macro_f1": f1v}
                if mname == "baseline":
                    alphas[mname][tag][h]["C"] = C
    return out, alphas


def evaluate(pr, decision, Y, lab, G, eval_mask, n_boot, seed):
    res, samples = {}, {}
    for sname, sfn in SUBSETS.items():
        res[sname], samples[sname] = {}, {}
        for k, h in enumerate(HEAD_NAMES):
            m = eval_mask & sfn(lab) & (Y[:, k] >= 0)
            y, p, pred = Y[m, k], pr["P"][h][m], pr[f"pred_{decision}"][h][m]
            ncls = len(HEADS[h]["classes"])
            extra = lab.infection_high.to_numpy()[m] if h == "infection" else None
            boot, smp = cluster_bootstrap(y, p, G[m], ncls, CRITICAL_CLASS[h], n_boot, seed, extra, pred)
            res[sname][h] = {"n": int(m.sum()), "n_groups": int(len(np.unique(G[m]))),
                             "class_counts": np.bincount(y, minlength=ncls).tolist(), **boot,
                             **per_class_table(y, p, HEADS[h]["classes"], pred)}
            if h == "infection":
                res[sname][h]["n_high"] = int(extra.sum())
            samples[sname][h] = smp
    return res, samples


def confusion_figure(res, title, path):
    fig, axes = plt.subplots(1, len(HEAD_NAMES), figsize=(4 * len(HEAD_NAMES), 3.6))
    for ax, h in zip(axes, HEAD_NAMES):
        cm = np.array(res[h]["confusion_matrix"])
        ax.imshow(cm, cmap="Blues")
        cls = HEADS[h]["classes"]
        for i in range(len(cls)):
            for j in range(len(cls)):
                ax.text(j, i, cm[i, j], ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=10)
        ax.set_xticks(range(len(cls)), cls, rotation=30, fontsize=8)
        ax.set_yticks(range(len(cls)), cls, fontsize=8)
        ax.set_xlabel("predicted")
        ax.set_ylabel("true")
        f1 = res[h]["macro_f1"]
        ax.set_title(f"{h}\nmacro F1 {f1['value']:.2f} [{f1['ci95'][0]:.2f}, {f1['ci95'][1]:.2f}]", fontsize=9)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def fmt(m):
    return f"{m['value']:.2f} [{m['ci95'][0]:.2f}, {m['ci95'][1]:.2f}]" if not np.isnan(m["value"]) else "n/a"


def fmt_diff(d):
    return f"{d['mean_diff']:+.2f} [{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}]"


def source_probe(cfg, X, Y, src, G, fold, images, device, seed, n_boot):
    C_grid = cfg["baseline"]["C_grid"]
    probe = {"n": len(src), "n_positive": int(src.sum())}
    P, C = oof_logreg(X, src, G, fold, C_grid, seed, score="auroc")
    probe["frozen_pretrained"] = {"auroc": cluster_bootstrap(src, P, G, 2, 1, n_boot, seed)[0]["auroc"], "C": C}
    P_ft = np.zeros((len(src), 2))
    for k in range(cfg["cv"]["n_splits"]):
        ck = torch.load(ROOT / cfg["checkpoint_dir"] / cfg["name"] / f"cv{k}.pt", weights_only=False,
                        map_location=device)
        model = MultiTaskNet(cfg["backbone"], {h: len(HEADS[h]["classes"]) for h in HEAD_NAMES},
                             pretrained=False).to(device)
        model.load_state_dict(ck["state_dict"])
        _, F = predict(model, images, Y, np.arange(len(src)), cfg, device, return_features=True)
        tr, te = np.where(fold != k)[0], np.where(fold == k)[0]
        m, _ = fit_lr_select_C(F[tr], src[tr], G[tr], C_grid, seed + k, score="auroc")
        P_ft[te] = m.predict_proba(F[te])
    probe["finetuned_cv_models"] = {"auroc": cluster_bootstrap(src, P_ft, G, 2, 1, n_boot, seed)[0]["auroc"]}
    return probe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/phase2_convnext_tiny.yaml")
    args = ap.parse_args()
    cfg = load_config(ROOT / args.config)
    seed = cfg["seed"]
    set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    n_boot = cfg["eval"]["n_boot"]

    proc = ROOT / cfg["processed_dir"]
    res_root = ROOT / cfg["results_dir"]
    out_dir = res_root / cfg["name"]
    df = pd.read_parquet(proc / "surgwound.parquet")
    splits = pd.read_csv(res_root / "splits.csv")
    assert (splits.image_name == df.image_name).all()
    inner = json.loads((res_root / "inner_splits.json").read_text(encoding="utf-8"))
    lab = encode_labels(df)
    Y = label_matrix(lab)
    G = splits.group.to_numpy()
    fold = splits.cv_fold.to_numpy()
    names = df.image_name.to_numpy()
    images = load_images(cfg, ROOT, names)
    lg = pd.read_parquet(out_dir / "logits.parquet")

    variant = cfg.get("image_variant", "original")
    fcache = proc / (f"frozen_{cfg['backbone']}_{cfg['input_size']}.npy" if variant == "original"
                     else f"frozen_{cfg['backbone']}_{cfg['input_size']}_{variant}.npy")
    if fcache.exists():
        X = np.load(fcache)
    else:
        print("[baseline] extracting frozen features")
        X = frozen_features(cfg["backbone"], images, np.arange(len(df)), cfg, device)
        np.save(fcache, X)

    preds, alphas = build_predictions(cfg, lab, Y, G, names, inner, lg, X, seed)
    masks = {"cv": fold >= 0, "secondary": (splits.secondary_role == "test").to_numpy()}

    results, comparisons = {}, {}
    for proto in ("cv", "secondary"):
        results[proto], comparisons[proto] = {}, {}
        for dec in DECISIONS:
            r = {m: evaluate(preds[m][proto], dec, Y, lab, G, masks[proto], n_boot, seed) for m in MODELS}
            results[proto][dec] = {m: r[m][0] for m in MODELS}
            comparisons[proto][dec] = {
                s: {h: {met: paired_diff_ci(r["finetuned"][1][s][h], r["baseline"][1][s][h], met)
                        for met in ("macro_f1", "critical_auroc", "critical_recall")}
                    for h in HEAD_NAMES} for s in SUBSETS}
            if dec == "tuned":
                for m in MODELS:
                    for s in SUBSETS:
                        confusion_figure(r[m][0][s], f"{MODELS[m]}, {proto}, {s}, tuned decision rule",
                                         out_dir / f"confusion_{m}_{proto}_{s}.png")

    per_fold = {}
    for k in range(cfg["cv"]["n_splits"]):
        r, _ = evaluate(preds["finetuned"]["cv"], "tuned", Y, lab, G, fold == k, 1, seed)
        per_fold[k] = {h: r["all"][h]["macro_f1"]["value"] for h in HEAD_NAMES}

    probe = source_probe(cfg, X, Y, lab.source_900plus.to_numpy(), G, fold, images, device, seed, n_boot)

    save_json({"results": results, "finetuned_minus_baseline": comparisons, "alphas": alphas,
               "per_fold_macro_f1_finetuned_tuned": per_fold, "source_probe": probe},
              out_dir / "metrics.json")
    md = render_markdown(results, comparisons, alphas, per_fold, probe)
    (out_dir / "metrics.md").write_text(md, encoding="utf-8")
    print(md)


def render_markdown(results, comparisons, alphas, per_fold, probe):
    L = []
    titles = {"cv": "Primary: grouped 5-fold CV, pooled out-of-fold",
              "secondary": "Secondary: official test minus leaked images"}
    for proto in ("cv", "secondary"):
        R = results[proto]["tuned"]
        D = comparisons[proto]["tuned"]
        L.append(f"## {titles[proto]} (tuned decision rule)\n")
        L.append("Infection: the ID 900+ excluded estimate comes first and is the primary honest estimate.\n")
        L.append("| head | subset | n | macro F1 FT | macro F1 baseline | diff (paired) | "
                 "critical AUROC FT | critical AUROC baseline | diff (paired) |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for h in HEAD_NAMES:
            order = ("excl_900plus", "all") if h == "infection" else ("all", "excl_900plus")
            for s in order:
                f, b, d = R["finetuned"][s][h], R["baseline"][s][h], D[s][h]
                L.append(f"| {h} ({HEADS[h]['classes'][CRITICAL_CLASS[h]]}) | {s} | {f['n']} | "
                         f"{fmt(f['macro_f1'])} | {fmt(b['macro_f1'])} | {fmt_diff(d['macro_f1'])} | "
                         f"{fmt(f['critical_auroc'])} | {fmt(b['critical_auroc'])} | {fmt_diff(d['critical_auroc'])} |")
        L.append("")
        L.append("| head | subset | critical recall FT | critical recall baseline | balanced acc FT | balanced acc baseline |")
        L.append("|---|---|---|---|---|---|")
        for h in HEAD_NAMES:
            for s in ("excl_900plus", "all"):
                f, b = R["finetuned"][s][h], R["baseline"][s][h]
                L.append(f"| {h} | {s} | {fmt(f['critical_recall'])} | {fmt(b['critical_recall'])} | "
                         f"{fmt(f['balanced_accuracy'])} | {fmt(b['balanced_accuracy'])} |")
        for s in ("excl_900plus", "all"):
            f, b = R["finetuned"][s]["infection"], R["baseline"][s]["infection"]
            L.append(f"\nHigh-risk images predicted elevated ({s}, n High = {f['n_high']}): "
                     f"fine-tuned {fmt(f['critical_recall_subset'])}, baseline {fmt(b['critical_recall_subset'])}")
        A = results[proto]["argmax"]
        L.append("\nFor reference, plain argmax macro F1 (FT / baseline, all): " + ", ".join(
            f"{h} {A['finetuned']['all'][h]['macro_f1']['value']:.2f} / {A['baseline']['all'][h]['macro_f1']['value']:.2f}"
            for h in HEAD_NAMES) + "\n")
    L.append("## Learned decision-rule alphas (0 = argmax, 1 = full prior correction)\n")
    L.append("| model | split | " + " | ".join(HEAD_NAMES) + " |")
    L.append("|---|---|" + "---|" * len(HEAD_NAMES))
    for m in MODELS:
        for tag, d in alphas[m].items():
            L.append(f"| {MODELS[m]} | {tag} | " + " | ".join(f"{d[h]['alpha']:.2f}" for h in HEAD_NAMES) + " |")
    L.append("\n## Source probe (ID 900+ vs rest), grouped 5-fold CV\n")
    L.append(f"n = {probe['n']}, positives = {probe['n_positive']}. Frozen pretrained features AUROC "
             f"{fmt(probe['frozen_pretrained']['auroc'])}; fine-tuned features AUROC "
             f"{fmt(probe['finetuned_cv_models']['auroc'])}.\n")
    L.append("## Per-fold macro F1 (fine-tuned, tuned rule)\n")
    L.append(pd.DataFrame(per_fold).T.round(2).to_markdown())
    return "\n".join(L)


if __name__ == "__main__":
    main()
