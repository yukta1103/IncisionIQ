"""Phase 4: calibration, infection operating points and abstention (model A).

Everything is fit per outer fold on that fold's inner-val split and evaluated on
pooled out-of-fold predictions. Every result is reported on all images and
excluding IDs 900+, with group-bootstrap 95% CIs.

Outputs in results/phase4/: metrics.json, tables.md, temperatures.json,
reliability_*.png, operating_points_*.png, abstention_*.png.

Usage: python scripts/phase4_calibrate.py [--config configs/phase3_convnext_tiny_inpainted.yaml]
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
from sklearn.metrics import roc_curve

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import CRITICAL_CLASS, HEAD_NAMES, HEADS, encode_labels, label_matrix  # noqa: E402
from src.eval.calibration import (brier, class_ece, ece, fit_temperature, group_bootstrap, nll,  # noqa: E402
                                  reliability_bins, threshold_for_recall)
from src.eval.metrics import softmax  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402

RECALL_TARGETS = (0.7, 0.8, 0.9)
COVERAGE_TARGETS = (1.0, 0.9, 0.8, 0.7)
SUBSETS = ("excl_900plus", "all")
OUT = ROOT / "results" / "phase4"


def logits_matrix(lg, names, rows_mask, h):
    cols = [c for c in lg.columns if c.startswith(f"{h}_logit")]
    sub = lg[rows_mask].set_index("image_name")
    return sub.loc[names, cols].to_numpy()


def fmt(m, d=2):
    return f"{m['value']:.{d}f} [{m['ci95'][0]:.{d}f}, {m['ci95'][1]:.{d}f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/phase3_convnext_tiny_inpainted.yaml")
    args = ap.parse_args()
    cfg = load_config(ROOT / args.config)
    seed, n_boot, K = cfg["seed"], cfg["eval"]["n_boot"], cfg["cv"]["n_splits"]
    set_seed(seed)
    OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(ROOT / cfg["processed_dir"] / "surgwound.parquet")
    lab = encode_labels(df)
    Y = label_matrix(lab)
    names = df.image_name.to_numpy()
    res = ROOT / cfg["results_dir"]
    splits = pd.read_csv(res / "splits.csv")
    G, fold = splits.group.to_numpy(), splits.cv_fold.to_numpy()
    inner = json.loads((res / "inner_splits.json").read_text(encoding="utf-8"))
    lg = pd.read_parquet(res / cfg["name"] / "logits.parquet")
    idx_of = {n: i for i, n in enumerate(names)}
    src900 = lab.source_900plus.to_numpy() == 1
    high = lab.infection_high.to_numpy() == 1
    subset_mask = {"excl_900plus": ~src900, "all": np.ones(len(df), bool)}

    # ---- temperature scaling per head per fold (inner-val only)
    raw, cal, val = {}, {}, {}
    temps = {h: {} for h in HEAD_NAMES}
    for h in HEAD_NAMES:
        k_h = HEAD_NAMES.index(h)
        L = np.full((len(df), len(HEADS[h]["classes"])), np.nan)
        Lc = L.copy()
        val[h] = {}
        for k in range(K):
            r = (lg.protocol == "cv") & (lg.fold == k)
            va = np.array([idx_of[n] for n in inner[f"cv{k}"]["val"]])
            ev = np.where(fold == k)[0]
            lv = logits_matrix(lg, names[va], r & (lg.role == "inner_val"), h)
            le = logits_matrix(lg, names[ev], r & (lg.role == "eval"), h)
            m = Y[va, k_h] >= 0
            T = fit_temperature(lv[m], Y[va, k_h][m])
            temps[h][k] = {"T": T, "inner_val_n": int(m.sum()),
                           "inner_val_nll_before": nll(lv[m], Y[va, k_h][m]), "inner_val_nll_after": nll(lv[m], Y[va, k_h][m], T)}
            L[ev], Lc[ev] = le, le / T
            val[h][k] = {"idx": va, "p_cal": softmax(lv / T)}
        raw[h], cal[h] = softmax(L), softmax(Lc)
    save_json(temps, OUT / "temperatures.json")

    out = {"calibration": {}, "operating_points": {}, "abstention": {}}
    md = ["# Phase 4 tables (model A, grouped 5-fold CV, out-of-fold)\n"]

    # ---- calibration metrics before / after
    md.append("## Calibration: before vs after temperature scaling\n")
    md.append("Top-label ECE uses 10 equal-width confidence bins. Class ECE is the calibration of P(critical class).\n")
    md.append("| head | subset | n | ECE before | ECE after | ECE diff (paired) | class ECE before | class ECE after | NLL before | NLL after | Brier before | Brier after |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for h in HEAD_NAMES:
        k_h, c = HEAD_NAMES.index(h), CRITICAL_CLASS[h]
        out["calibration"][h] = {}
        for s in SUBSETS:
            m = subset_mask[s] & (Y[:, k_h] >= 0)
            y, pr, pc, g = Y[m, k_h], raw[h][m], cal[h][m], G[m]

            def stat(i, y=y, pr=pr, pc=pc, c=c):
                yc = (y[i] == c).astype(float)
                return {"ece_before": ece(pr[i], y[i]), "ece_after": ece(pc[i], y[i]),
                        "ece_diff": ece(pc[i], y[i]) - ece(pr[i], y[i]),
                        "class_ece_before": class_ece(pr[i][:, c], yc), "class_ece_after": class_ece(pc[i][:, c], yc),
                        "nll_before": float(-np.log(np.clip(pr[i][np.arange(len(i)), y[i]], 1e-12, None)).mean()),
                        "nll_after": float(-np.log(np.clip(pc[i][np.arange(len(i)), y[i]], 1e-12, None)).mean()),
                        "brier_before": brier(pr[i], y[i]), "brier_after": brier(pc[i], y[i])}
            b = group_bootstrap(stat, len(y), g, n_boot, seed)
            out["calibration"][h][s] = {"n": int(m.sum()), **b,
                                        "reliability_before": reliability_bins(pr[:, c], (y == c).astype(float)),
                                        "reliability_after": reliability_bins(pc[:, c], (y == c).astype(float))}
            d = b["ece_diff"]
            md.append(f"| {h} | {s} | {m.sum()} | {fmt(b['ece_before'], 3)} | {fmt(b['ece_after'], 3)} | "
                      f"{d['value']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] | {fmt(b['class_ece_before'], 3)} | "
                      f"{fmt(b['class_ece_after'], 3)} | {fmt(b['nll_before'], 3)} | {fmt(b['nll_after'], 3)} | "
                      f"{fmt(b['brier_before'], 3)} | {fmt(b['brier_after'], 3)} |")
    md.append("\nTemperatures per fold (T > 1 means the model was overconfident):\n")
    md.append("| head | " + " | ".join(f"fold {k}" for k in range(K)) + " |")
    md.append("|---|" + "---|" * K)
    for h in HEAD_NAMES:
        md.append(f"| {h} | " + " | ".join(f"{temps[h][k]['T']:.2f}" for k in range(K)) + " |")

    for s in SUBSETS:
        fig, axes = plt.subplots(2, len(HEAD_NAMES), figsize=(4.2 * len(HEAD_NAMES), 7.5),
                                 gridspec_kw={"height_ratios": [3, 1]})
        for j, h in enumerate(HEAD_NAMES):
            r = out["calibration"][h][s]
            ax = axes[0, j]
            ax.plot([0, 1], [0, 1], color="0.6", lw=1, ls="--")
            for key, col, lbl in (("reliability_before", "#c44e52", "before"), ("reliability_after", "#4c72b0", "after")):
                rb = [b for b in r[key] if b["n"] > 0]
                ax.plot([b["mean_pred"] for b in rb], [b["frac_pos"] for b in rb], "o-", color=col, label=lbl, ms=4)
            crit = HEADS[h]["classes"][CRITICAL_CLASS[h]]
            ax.set_title(f"{h}: P({crit})\nclass ECE {r['class_ece_before']['value']:.3f} -> {r['class_ece_after']['value']:.3f}", fontsize=9)
            ax.set_xlabel("mean predicted probability")
            ax.set_ylabel("observed frequency")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.legend(fontsize=8, loc="upper left")
            axh = axes[1, j]
            ns = [b["n"] for b in r["reliability_after"]]
            axh.bar(np.arange(10) / 10 + 0.05, ns, width=0.09, color="#4c72b0")
            axh.set_xlim(0, 1)
            axh.set_xlabel("P(critical), after scaling")
            axh.set_ylabel("images")
        fig.suptitle(f"Reliability of P(critical class), grouped CV out-of-fold, {s} (n per head in metrics)", fontsize=10)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(OUT / f"reliability_{s}.png", dpi=110)
        plt.close(fig)

    # ---- infection operating points by recall target (thresholds from inner-val)
    h, k_h = "infection", HEAD_NAMES.index("infection")
    p_el = cal[h][:, 1]
    thresholds = {t: {} for t in RECALL_TARGETS}
    for t in RECALL_TARGETS:
        for k in range(K):
            va, pv = val[h][k]["idx"], val[h][k]["p_cal"][:, 1]
            pos = Y[va, k_h] == 1
            thresholds[t][k] = {"threshold": threshold_for_recall(pv[pos], t), "inner_val_positives": int(pos.sum())}
    md.append("\n## Infection operating points (threshold per fold chosen on inner-val to reach the recall target)\n")
    md.append("False alarms = Low-risk images flagged Elevated. Per 100 = per 100 images of that subset.\n")
    md.append("| target | subset | n | recall (Elevated) | High-risk recall | specificity | PPV | flagged per 100 | false alarms per 100 | false alarms per Elevated caught |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for t in RECALL_TARGETS:
        thr = np.array([thresholds[t][f]["threshold"] for f in fold])
        dec = (p_el >= thr).astype(int)
        out["operating_points"][str(t)] = {"thresholds": thresholds[t]}
        for s in SUBSETS:
            m = subset_mask[s]
            y, d, hi, g = Y[m, k_h], dec[m], high[m], G[m]

            def stat(i, y=y, d=d, hi=hi):
                yy, dd = y[i], d[i]
                tp, fp = int(((dd == 1) & (yy == 1)).sum()), int(((dd == 1) & (yy == 0)).sum())
                pos, neg = int((yy == 1).sum()), int((yy == 0).sum())
                return {"recall": tp / pos if pos else np.nan, "specificity": 1 - fp / neg if neg else np.nan,
                        "ppv": tp / (tp + fp) if tp + fp else np.nan, "flagged_per_100": 100 * dd.mean(),
                        "false_alarms_per_100": 100 * fp / len(i), "fa_per_tp": fp / tp if tp else np.nan,
                        "high_recall": float(dd[hi[i]].mean()) if hi[i].any() else np.nan}
            b = group_bootstrap(stat, int(m.sum()), g, n_boot, seed)
            counts = {"n": int(m.sum()), "n_elevated": int((y == 1).sum()), "n_high": int(hi.sum()),
                      "tp": int(((d == 1) & (y == 1)).sum()), "fp": int(((d == 1) & (y == 0)).sum())}
            out["operating_points"][str(t)][s] = {**counts, **b}
            md.append(f"| {t:.1f} | {s} | {counts['n']} | {fmt(b['recall'])} | {fmt(b['high_recall'])} (n={counts['n_high']}) | "
                      f"{fmt(b['specificity'])} | {fmt(b['ppv'])} | {fmt(b['flagged_per_100'], 1)} | "
                      f"{fmt(b['false_alarms_per_100'], 1)} | {fmt(b['fa_per_tp'], 1)} |")
    md.append("\nPer-fold thresholds on calibrated P(elevated) (inner-val positives per fold in brackets):\n")
    md.append("| target | " + " | ".join(f"fold {k}" for k in range(K)) + " |")
    md.append("|---|" + "---|" * K)
    for t in RECALL_TARGETS:
        md.append(f"| {t:.1f} | " + " | ".join(f"{thresholds[t][k]['threshold']:.3f} ({thresholds[t][k]['inner_val_positives']})"
                                               for k in range(K)) + " |")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, s in zip(axes, SUBSETS):
        m = subset_mask[s]
        fpr, tpr, _ = roc_curve(Y[m, k_h], p_el[m])
        neg_rate = (Y[m, k_h] == 0).mean()
        ax.plot(100 * fpr * neg_rate, tpr, color="0.4", lw=1.5, label="all thresholds (descriptive, pooled OOF)")
        for t, col in zip(RECALL_TARGETS, ("#55a868", "#dd8452", "#c44e52")):
            r = out["operating_points"][str(t)][s]
            ax.errorbar(r["false_alarms_per_100"]["value"], r["recall"]["value"],
                        xerr=[[r["false_alarms_per_100"]["value"] - r["false_alarms_per_100"]["ci95"][0]],
                              [r["false_alarms_per_100"]["ci95"][1] - r["false_alarms_per_100"]["value"]]],
                        yerr=[[r["recall"]["value"] - r["recall"]["ci95"][0]], [r["recall"]["ci95"][1] - r["recall"]["value"]]],
                        fmt="o", color=col, capsize=3, label=f"target {t:.1f} (inner-val threshold)")
            ax.axhline(t, color=col, lw=0.6, ls=":")
        ax.set_xlabel("false alarms per 100 images")
        ax.set_ylabel("recall on Elevated risk")
        ax.set_title(f"Infection operating points, {s} (n = {int(m.sum())})", fontsize=10)
        ax.set_ylim(0, 1.02)
        ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "operating_points.png", dpi=110)
    plt.close(fig)

    # ---- abstention
    # Infection: decision at the 0.8 recall operating point. A "flag Elevated" decision already goes to a
    # clinician, so only "Low" calls can be referred; their confidence is 1 - P(elevated). A referred
    # Elevated case is not a miss. Other heads: calibrated argmax and top-label confidence.
    md.append("\n## Abstention (send for review when confidence < tau)\n")
    md.append("tau per fold is the inner-val confidence quantile that gives the target coverage; results are out-of-fold.\n")
    thr08 = np.array([thresholds[0.8][f]["threshold"] for f in fold])
    dec08 = (p_el >= thr08).astype(int)
    conf = {}
    for hh in HEAD_NAMES:
        conf[hh] = cal[hh].max(1)
    conf["infection"] = np.where(dec08 == 1, 1.0, 1 - p_el)

    def val_conf(hh, k):
        pv = val[hh][k]["p_cal"]
        if hh != "infection":
            return pv.max(1)
        d = (pv[:, 1] >= thresholds[0.8][k]["threshold"]).astype(int)
        return np.where(d == 1, 1.0, 1 - pv[:, 1])

    md.append("### Infection (decision at the 0.8 recall operating point)\n")
    md.append("Only Low calls can be referred (a flag already goes to a clinician). Missed = Elevated, called Low and "
              "not referred. Workload = flagged + referred, per 100 images.\n")
    md.append("| target coverage | subset | coverage | missed Elevated per 100 | Elevated caught or referred | High-risk caught or referred | workload per 100 | accuracy on answered |")
    md.append("|---|---|---|---|---|---|---|---|")
    for cov in COVERAGE_TARGETS:
        taus = {k: (float(np.quantile(val_conf("infection", k), 1 - cov)) if cov < 1 else 0.0) for k in range(K)}
        tau = np.array([taus[f] for f in fold])
        refer = conf["infection"] < tau
        out["abstention"].setdefault("infection", {})[str(cov)] = {"tau_per_fold": taus}
        for s in SUBSETS:
            m = subset_mask[s]
            y, d, rf, hi, g = Y[m, k_h], dec08[m], refer[m], high[m], G[m]

            def stat(i, y=y, d=d, rf=rf, hi=hi):
                yy, dd, rr = y[i], d[i], rf[i]
                pos = yy == 1
                ans = ~rr
                return {"coverage": ans.mean(), "missed_per_100": 100 * (pos & (dd == 0) & ans).mean(),
                        "effective_recall": ((dd == 1) | rr)[pos].mean() if pos.any() else np.nan,
                        "high_effective_recall": ((dd == 1) | rr)[hi[i]].mean() if hi[i].any() else np.nan,
                        "workload_per_100": 100 * ((dd == 1) | rr).mean(),
                        "accuracy_answered": (dd[ans] == yy[ans]).mean() if ans.any() else np.nan}
            b = group_bootstrap(stat, int(m.sum()), g, n_boot, seed)
            out["abstention"]["infection"][str(cov)][s] = {"n_high": int(hi.sum()), **b}
            md.append(f"| {cov:.1f} | {s} | {fmt(b['coverage'])} | {fmt(b['missed_per_100'], 1)} | {fmt(b['effective_recall'])} | "
                      f"{fmt(b['high_effective_recall'])} (n={int(hi.sum())}) | {fmt(b['workload_per_100'], 1)} | {fmt(b['accuracy_answered'])} |")

    md.append("\n### Other heads (calibrated argmax)\n")
    md.append("| head | target coverage | subset | coverage | accuracy on answered | critical recall on answered | critical cases referred |")
    md.append("|---|---|---|---|---|---|---|")
    for hh in ("erythema", "edema", "exudate"):
        k_hh, c = HEAD_NAMES.index(hh), CRITICAL_CLASS[hh]
        pred = cal[hh].argmax(1)
        for cov in COVERAGE_TARGETS:
            taus = {k: (float(np.quantile(val_conf(hh, k), 1 - cov)) if cov < 1 else 0.0) for k in range(K)}
            tau = np.array([taus[f] for f in fold])
            refer = conf[hh] < tau
            out["abstention"].setdefault(hh, {})[str(cov)] = {"tau_per_fold": taus}
            for s in ("all",):
                m = subset_mask[s] & (Y[:, k_hh] >= 0)
                y, d, rf, g = Y[m, k_hh], pred[m], refer[m], G[m]

                def stat(i, y=y, d=d, rf=rf, c=c):
                    yy, dd, rr = y[i], d[i], rf[i]
                    ans = ~rr
                    cm = yy == c
                    return {"coverage": ans.mean(), "accuracy_answered": (dd[ans] == yy[ans]).mean() if ans.any() else np.nan,
                            "critical_recall_answered": (dd[ans & cm] == c).mean() if (ans & cm).any() else np.nan,
                            "critical_referred": rr[cm].mean() if cm.any() else np.nan}
                b = group_bootstrap(stat, int(m.sum()), g, n_boot, seed)
                out["abstention"][hh][str(cov)][s] = b
                md.append(f"| {hh} | {cov:.1f} | {s} | {fmt(b['coverage'])} | {fmt(b['accuracy_answered'])} | "
                          f"{fmt(b['critical_recall_answered'])} | {fmt(b['critical_referred'])} |")

    # descriptive curves over the full range of tau (pooled OOF)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    grid = np.linspace(0.0, 1.0001, 201)
    for s, ls in (("excl_900plus", "-"), ("all", "--")):
        m = subset_mask[s]
        y, d, cf, hi = Y[m, k_h], dec08[m], conf["infection"][m], high[m]
        cov_, acc_, eff_, heff_ = [], [], [], []
        for tau in grid:
            rr = cf < tau
            ans = ~rr
            cov_.append(ans.mean())
            acc_.append(100 * ((y == 1) & (d == 0) & ans).mean())
            eff_.append(((d == 1) | rr)[y == 1].mean())
            heff_.append(((d == 1) | rr)[hi].mean())
        axes[0].plot(cov_, acc_, ls, color="#c44e52", label=f"{s}")
        axes[1].plot(cov_, eff_, ls, color="#c44e52", label=f"Elevated, {s}")
        axes[1].plot(cov_, heff_, ls, color="#8172b2", label=f"High-risk, {s} (n={int(hi.sum())})")
        axes[2].plot(cov_, 100 * np.array([((d == 1) | (cf < tau)).mean() for tau in grid]), ls, color="#55a868", label=s)
    for cov in COVERAGE_TARGETS[1:]:
        for ax in axes:
            ax.axvline(cov, color="0.8", lw=0.8)
    axes[0].set_ylabel("missed Elevated per 100 images")
    axes[1].set_ylabel("caught (flagged) or referred")
    axes[2].set_ylabel("workload: flagged + referred per 100")
    for ax, t in zip(axes, ("Infection: coverage vs missed Elevated", "Infection: coverage vs Elevated / High-risk caught",
                            "Infection: coverage vs clinician workload")):
        ax.set_xlabel("coverage (share answered automatically)")
        ax.set_title(t, fontsize=10)
        ax.invert_xaxis()
        ax.legend(fontsize=7)
    fig.suptitle("Abstention curves (decision at the 0.8 recall operating point; descriptive, pooled OOF)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "abstention_infection.png", dpi=110)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, hh in zip(axes, ("erythema", "edema", "exudate")):
        k_hh, c = HEAD_NAMES.index(hh), CRITICAL_CLASS[hh]
        m = Y[:, k_hh] >= 0
        y, pr, cf = Y[m, k_hh], cal[hh][m].argmax(1), conf[hh][m]
        cov_, acc_, rec_ = [], [], []
        for tau in np.linspace(cf.min(), 1.0, 60):
            ans = cf >= tau
            if ans.sum() < 20:
                break
            cov_.append(ans.mean())
            acc_.append((pr[ans] == y[ans]).mean())
            cm = ans & (y == c)
            rec_.append((pr[cm] == c).mean() if cm.any() else np.nan)
        ax.plot(cov_, acc_, color="#4c72b0", label="accuracy on answered")
        ax.plot(cov_, rec_, color="#c44e52", label=f"{HEADS[hh]['classes'][c]} recall on answered")
        ax.set_title(f"{hh} (all images, n = {int(m.sum())})", fontsize=10)
        ax.set_xlabel("coverage")
        ax.invert_xaxis()
        ax.set_ylim(0, 1)
        ax.legend(fontsize=7)
    fig.suptitle("Abstention curves for the other heads (calibrated argmax; descriptive, pooled OOF)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / "abstention_other_heads.png", dpi=110)
    plt.close(fig)

    save_json(out, OUT / "metrics.json")
    (OUT / "tables.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
