"""One-parameter decision rule per head, learned on inner-val only.

score_c = log p_c - alpha * log prior_c, prediction = argmax_c score_c.
alpha = 0 is plain argmax, alpha = 1 is full prior correction (the Bayes rule
for balanced error). For a binary head this is exactly a probability threshold.
A single parameter is used instead of free per-class thresholds because the
inner-val slices hold as few as 1 to 7 examples of the rarest classes.
"""
import numpy as np
from sklearn.metrics import f1_score

ALPHA_GRID = np.round(np.arange(0.0, 2.0001, 0.05), 2)


def adjusted_pred(p: np.ndarray, prior: np.ndarray, alpha: float) -> np.ndarray:
    return (np.log(np.clip(p, 1e-12, None)) - alpha * np.log(prior)).argmax(1)


def fit_alpha(y: np.ndarray, p: np.ndarray, prior: np.ndarray) -> tuple[float, float]:
    """Return (alpha, inner-val macro F1). Among tied maxima the median alpha is
    taken, which is more stable than the first or last."""
    k = p.shape[1]
    scores = np.array([f1_score(y, adjusted_pred(p, prior, a), labels=list(range(k)),
                                average="macro", zero_division=0) for a in ALPHA_GRID])
    best = np.flatnonzero(np.isclose(scores, scores.max()))
    a = float(ALPHA_GRID[best[len(best) // 2]])
    return a, float(scores.max())


def class_prior(y: np.ndarray, k: int) -> np.ndarray:
    y = y[y >= 0]
    c = np.bincount(y, minlength=k).astype(float) + 1.0  # add-one so no class has prior 0
    return c / c.sum()
