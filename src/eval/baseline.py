"""Frozen-feature baselines and probes.

Logistic regression on frozen pretrained backbone features, using exactly the
same outer folds as the fine-tuned model. C is chosen by grouped inner CV on
the outer training portion only.
"""
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.data.dataset import WoundDataset, build_transforms


@torch.no_grad()
def frozen_features(backbone_name, images, idx, cfg, device):
    import timm
    from torch.utils.data import DataLoader

    model = timm.create_model(backbone_name, pretrained=True, num_classes=0).to(device).eval()
    dummy = np.zeros((len(images), 1), dtype=int)
    dl = DataLoader(WoundDataset(images, dummy, idx, build_transforms(cfg, train=False)),
                    batch_size=cfg["eval_batch_size"], shuffle=False)
    out = []
    for x, _, _ in dl:
        with torch.autocast("cuda", dtype=torch.float16, enabled=device == "cuda"):
            out.append(model(x.to(device)).float().cpu())
    return torch.cat(out).numpy()


def _lr(C, seed):
    return make_pipeline(StandardScaler(), LogisticRegression(
        C=C, class_weight="balanced", max_iter=5000, random_state=seed))


def fit_lr_select_C(X, y, groups, C_grid, seed, score="macro_f1", n_inner=3):
    """Pick C by grouped inner CV, refit on all of X."""
    best_C, best_s = C_grid[0], -np.inf
    n_inner = min(n_inner, len(np.unique(groups)))
    for C in C_grid:
        scores = []
        cv = StratifiedGroupKFold(n_splits=n_inner, shuffle=True, random_state=seed)
        for tr, va in cv.split(X, y, groups):
            if len(np.unique(y[tr])) < len(np.unique(y)):
                continue
            m = _lr(C, seed).fit(X[tr], y[tr])
            if score == "auroc":
                if len(np.unique(y[va])) < 2:
                    continue
                scores.append(roc_auc_score(y[va], m.predict_proba(X[va])[:, 1]))
            else:
                scores.append(f1_score(y[va], m.predict(X[va]), average="macro", zero_division=0))
        s = np.mean(scores) if scores else -np.inf
        if s > best_s:
            best_C, best_s = C, s
    return _lr(best_C, seed).fit(X, y), best_C


def oof_logreg(X, y, groups, fold, C_grid, seed, score="macro_f1"):
    """Out-of-fold probabilities. Rows with y < 0 are unlabeled: they get
    predictions but are never used for fitting."""
    n_classes = int(y.max()) + 1
    P = np.full((len(y), n_classes), np.nan)
    chosen = {}
    for k in np.unique(fold):
        tr = np.where((fold != k) & (y >= 0))[0]
        te = np.where(fold == k)[0]
        m, C = fit_lr_select_C(X[tr], y[tr], groups[tr], C_grid, seed + int(k), score)
        proba = np.zeros((len(te), n_classes))
        proba[:, m.classes_] = m.predict_proba(X[te])
        P[te] = proba
        chosen[int(k)] = C
    return P, chosen
