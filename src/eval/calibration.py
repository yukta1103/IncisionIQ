"""Temperature scaling, calibration metrics and operating points.

All fitting happens on a fold's inner-val split; evaluation is on out-of-fold
predictions only.
"""
import numpy as np
from scipy.optimize import minimize_scalar

from src.eval.metrics import softmax


def nll(logits: np.ndarray, y: np.ndarray, T: float = 1.0) -> float:
    p = softmax(logits / T)
    return float(-np.log(np.clip(p[np.arange(len(y)), y], 1e-12, None)).mean())


def fit_temperature(logits: np.ndarray, y: np.ndarray, bounds=(0.05, 20.0)) -> float:
    """Single temperature minimizing NLL, searched on log T."""
    res = minimize_scalar(lambda lt: nll(logits, y, float(np.exp(lt))),
                          bounds=(np.log(bounds[0]), np.log(bounds[1])), method="bounded")
    return float(np.exp(res.x))


def ece(p: np.ndarray, y: np.ndarray, n_bins: int = 10) -> float:
    """Top-label expected calibration error with equal-width confidence bins."""
    conf = p.max(1)
    correct = (p.argmax(1) == y).astype(float)
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(conf, edges[1:-1]), 0, n_bins - 1)
    total = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return float(total)


def class_ece(p_c: np.ndarray, y_c: np.ndarray, n_bins: int = 10) -> float:
    """Calibration error of P(class c) against the event y == c (binary reliability)."""
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p_c, edges[1:-1]), 0, n_bins - 1)
    total = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(y_c[m].mean() - p_c[m].mean())
    return float(total)


def brier(p: np.ndarray, y: np.ndarray) -> float:
    onehot = np.eye(p.shape[1])[y]
    return float(((p - onehot) ** 2).sum(1).mean())


def reliability_bins(p_c: np.ndarray, y_c: np.ndarray, n_bins: int = 10):
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p_c, edges[1:-1]), 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        m = idx == b
        rows.append({"lo": edges[b], "hi": edges[b + 1], "n": int(m.sum()),
                     "mean_pred": float(p_c[m].mean()) if m.any() else np.nan,
                     "frac_pos": float(y_c[m].mean()) if m.any() else np.nan})
    return rows


def threshold_for_recall(scores_pos: np.ndarray, target: float) -> float:
    """Largest threshold t such that the share of positives with score >= t is at
    least `target`. With few positives this is coarse; that is reported, not hidden."""
    s = np.sort(scores_pos)[::-1]
    k = int(np.ceil(target * len(s)))  # need at least k positives at or above t
    return float(s[max(k, 1) - 1])


def group_bootstrap(stat_fn, n: int, groups: np.ndarray, n_boot: int, seed: int):
    """Percentile CI of stat_fn(idx) over resamples of groups. stat_fn returns a dict."""
    rng = np.random.default_rng(seed)
    ug, inv = np.unique(groups, return_inverse=True)
    members = [np.where(inv == g)[0] for g in range(len(ug))]
    point = stat_fn(np.arange(n))
    samples = {k: [] for k in point}
    for _ in range(n_boot):
        idx = np.concatenate([members[g] for g in rng.integers(0, len(ug), len(ug))])
        for k, v in stat_fn(idx).items():
            samples[k].append(v)
    out = {}
    for k, v in point.items():
        a = np.array(samples[k], float)
        a = a[~np.isnan(a)]
        ci = [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) > n_boot // 2 else [np.nan, np.nan]
        out[k] = {"value": float(v), "ci95": ci}
    return out
