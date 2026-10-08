"""Per-head metrics with group (cluster) bootstrap confidence intervals.

Bootstrap resamples same-patient groups, not images, so correlated photos of
one patient do not shrink the interval artificially.
"""
import numpy as np
from sklearn.metrics import (balanced_accuracy_score, confusion_matrix, f1_score,
                             precision_recall_fscore_support, roc_auc_score)


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def _auroc(y, p, k):
    if len(np.unique(y)) < 2:
        return np.nan
    if k == 2:
        return roc_auc_score(y, p[:, 1])
    present = np.unique(y)
    if len(present) < k:
        return np.nan
    return roc_auc_score(y, p, multi_class="ovr", average="macro")


def scalar_metrics(y, p, k, critical, extra_mask=None, pred=None):
    """Metrics that get bootstrap CIs. `extra_mask` marks a subset (e.g. High-risk
    images) for which recall of `critical` is reported separately. `pred` overrides
    argmax decisions; AUROCs always use the raw probabilities `p`."""
    pred = p.argmax(1) if pred is None else pred
    labels = list(range(k))
    _, rec, _, sup = precision_recall_fscore_support(y, pred, labels=labels, zero_division=0)
    out = {
        "macro_f1": f1_score(y, pred, labels=labels, average="macro", zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y, pred) if len(np.unique(y)) > 1 else np.nan,
        "accuracy": float((pred == y).mean()),
        "auroc": _auroc(y, p, k),
        "critical_recall": rec[critical] if sup[critical] > 0 else np.nan,
        # threshold-free: one-vs-rest AUROC of the critical class
        "critical_auroc": (roc_auc_score(y == critical, p[:, critical])
                           if 0 < (y == critical).sum() < len(y) else np.nan),
    }
    if extra_mask is not None:
        m = extra_mask.astype(bool)
        out["critical_recall_subset"] = float((pred[m] == critical).mean()) if m.any() else np.nan
    return out


def cluster_bootstrap(y, p, groups, k, critical, n_boot, seed, extra_mask=None, pred=None):
    point = scalar_metrics(y, p, k, critical, extra_mask, pred)
    rng = np.random.default_rng(seed)
    ug, inv = np.unique(groups, return_inverse=True)
    members = [np.where(inv == g)[0] for g in range(len(ug))]
    samples = {m: [] for m in point}
    for _ in range(n_boot):
        pick = rng.integers(0, len(ug), len(ug))
        idx = np.concatenate([members[g] for g in pick])
        em = extra_mask[idx] if extra_mask is not None else None
        pr = pred[idx] if pred is not None else None
        for m, v in scalar_metrics(y[idx], p[idx], k, critical, em, pr).items():
            samples[m].append(v)
    out = {}
    for m, v in point.items():
        arr = np.array(samples[m], dtype=float)
        arr = arr[~np.isnan(arr)]
        lo, hi = (np.percentile(arr, [2.5, 97.5]) if len(arr) > 0.5 * n_boot else (np.nan, np.nan))
        out[m] = {"value": float(v), "ci95": [float(lo), float(hi)]}
    return out, samples


def per_class_table(y, p, classes, pred=None):
    pred = p.argmax(1) if pred is None else pred
    labels = list(range(len(classes)))
    prec, rec, f1, sup = precision_recall_fscore_support(y, pred, labels=labels, zero_division=0)
    return {
        "per_class": {c: {"precision": float(prec[i]), "recall": float(rec[i]), "f1": float(f1[i]),
                          "support": int(sup[i])} for i, c in enumerate(classes)},
        "confusion_matrix": confusion_matrix(y, pred, labels=labels).tolist(),
    }


def paired_diff_ci(samples_a, samples_b, metric):
    a = np.array(samples_a[metric], dtype=float)
    b = np.array(samples_b[metric], dtype=float)
    d = a - b
    d = d[~np.isnan(d)]
    return {"mean_diff": float(d.mean()), "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "frac_boot_a_better": float((d > 0).mean())}
