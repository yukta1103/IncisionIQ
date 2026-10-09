"""Per-image predictions for the fine-tuned model and the frozen baseline.

Both models are fit on each fold's inner-train split; each gets a per-head
decision rule learned on that fold's inner-val split (src/eval/thresholds.py).
"""
import numpy as np

from src.data.labels import HEAD_NAMES, HEADS
from src.eval.baseline import fit_lr_select_C
from src.eval.metrics import softmax
from src.eval.thresholds import adjusted_pred, class_prior, fit_alpha

MODELS = {"finetuned": "fine-tuned", "baseline": "frozen + logreg"}


def ft_probs(lg, tag_rows, names_idx, h):
    cols = [c for c in lg.columns if c.startswith(f"{h}_logit")]
    sub = tag_rows.set_index("image_name").loc[names_idx, cols]
    return softmax(sub.to_numpy())


def build_predictions(cfg, lab, Y, G, names, inner, lg, X, seed, with_baseline: bool = True):
    """For each model and protocol: raw probabilities on eval images, argmax and
    tuned decisions, and the learned alphas. `with_baseline=False` skips the
    logistic-regression baseline (X may then be None)."""
    idx_of = {n: i for i, n in enumerate(names)}
    models = MODELS if with_baseline else {"finetuned": MODELS["finetuned"]}
    out = {m: {p: {"P": {h: np.full((len(names), len(HEADS[h]["classes"])), np.nan) for h in HEAD_NAMES},
                   "pred_tuned": {h: np.full(len(names), -1) for h in HEAD_NAMES},
                   "pred_argmax": {h: np.full(len(names), -1) for h in HEAD_NAMES}}
               for p in ("cv", "secondary")} for m in models}
    alphas = {m: {} for m in models}
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
            runs = [("finetuned", pv_ft, pe_ft)]
            if with_baseline:
                # baseline: logistic regression fit on the same inner-train split
                trl = tr[Y[tr, k] >= 0]
                m, C = fit_lr_select_C(X[trl], Y[trl, k], G[trl], cfg["baseline"]["C_grid"], seed)
                pv_bl = np.zeros((len(va), ncls))
                pe_bl = np.zeros((len(ev), ncls))
                pv_bl[:, m.classes_] = m.predict_proba(X[va])
                pe_bl[:, m.classes_] = m.predict_proba(X[ev])
                runs.append(("baseline", pv_bl, pe_bl))
            for mname, pv, pe in runs:
                a, f1v = fit_alpha(yv[lv], pv[lv], prior)
                o = out[mname][proto]
                o["P"][h][ev] = pe
                o["pred_argmax"][h][ev] = pe.argmax(1)
                o["pred_tuned"][h][ev] = adjusted_pred(pe, prior, a)
                alphas[mname].setdefault(tag, {})[h] = {"alpha": a, "inner_val_macro_f1": f1v}
                if mname == "baseline":
                    alphas[mname][tag][h]["C"] = C
    return out, alphas
