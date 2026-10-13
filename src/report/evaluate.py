"""Claim-level scoring of report sets with group-bootstrap CIs.

Bootstraps work on per-image claim counts (supported, contradicted,
unverifiable), so each resample is a few array sums.
"""
import numpy as np
import pandas as pd

from src.eval.calibration import group_bootstrap
from src.report.claims import extract_claims
from src.report.faithfulness import expert_reference, score_claims
from src.report.template import source_reference


def score_reports(texts, sources, df) -> pd.DataFrame:
    """One row per claim: vs the source JSON (if given) and vs the expert labels.
    `texts[i]` is the report for df.iloc[i]; None means no report (failed request)."""
    rows = []
    for i, (t, src) in enumerate(zip(texts, sources)):
        if t is None:
            continue
        claims = extract_claims(t)
        if src is not None:
            for r in score_claims(claims, source_reference(src), mode="source", ignore=("infection_level",)):
                rows.append({"i": i, "against": "source", **r})
        for r in score_claims(claims, expert_reference(df.iloc[i]), mode="expert"):
            rows.append({"i": i, "against": "expert", **r})
    return pd.DataFrame(rows, columns=["i", "against", "attribute", "value", "reference", "status"])


def claim_counts(S: pd.DataFrame, n_images: int, against: str = "expert") -> np.ndarray:
    """(n_images, 3) array: supported, contradicted (incl. unsupported attribute), unverifiable."""
    s = S[S.against == against]
    out = np.zeros((n_images, 3))
    for col, statuses in enumerate((["supported"], ["contradicted", "unsupported_attribute"], ["unverifiable"])):
        c = s[s.status.isin(statuses)].groupby("i").size()
        out[c.index.to_numpy(), col] = c.to_numpy()
    return out


def rates(C: np.ndarray, missing: np.ndarray | None = None) -> dict:
    """Claim rates from per-image counts. `missing` (per image) adds incorrect claims
    for images without a usable report, e.g. refusals counted as incorrect; it only
    affects correctness."""
    sup, con, unv = C.sum(0)
    miss = float(missing.sum()) if missing is not None else 0.0
    total = sup + con + unv
    n = len(C)
    return {"claims_per_report": total / n if n else np.nan,
            "correctness": sup / (sup + con + miss) if sup + con + miss else np.nan,  # among verifiable claims
            "hallucination_rate": con / total if total else np.nan,           # contradicted share of all claims
            "unverifiable_share": unv / total if total else np.nan,
            "reports_with_contradiction": float((C[:, 1] > 0).mean()) if n else np.nan}


def boot_rates(S: pd.DataFrame, against: str, img_idx, G, n_boot: int, seed: int):
    idx = np.asarray(img_idx)
    C = claim_counts(S, len(G), against)[idx]
    return group_bootstrap(lambda ix: rates(C[ix]), len(idx), G[idx], n_boot, seed)


def paired_rate_diff(S_a: pd.DataFrame, S_b: pd.DataFrame, img_idx, G, n_boot: int, seed: int, metric: str):
    """a minus b on the same group resamples."""
    idx = np.asarray(img_idx)
    Ca, Cb = claim_counts(S_a, len(G))[idx], claim_counts(S_b, len(G))[idx]
    return group_bootstrap(lambda ix: {"diff": rates(Ca[ix])[metric] - rates(Cb[ix])[metric]},
                           len(idx), G[idx], n_boot, seed)["diff"]
