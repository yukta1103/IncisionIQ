"""From model probabilities to the attribute JSON used by the report and verdict.

Same rules as the evaluated system (Phases 2 to 5):
- erythema, edema, exudate: the per-head decision rule (argmax of
  log p - alpha * log prior), marked "uncertain" when the top probability is
  below the abstention cut-off tau (80% coverage, Phase 4);
- infection: the band from the flag-or-refer operating point
  (high concern >= t_flag > uncertain >= t_review > low concern), shown with
  the band's observed Elevated rate.

`params` is one fold's parameters: each image's own fold for the out-of-fold
evaluation, and fold 0 for every photo in the demo (examples and uploads).
"""
import numpy as np

from src.data.labels import HEADS
from src.eval.thresholds import adjusted_pred


def attributes_from_probs(probs: dict, params: dict, band_rates: dict) -> dict:
    """probs: head -> probability vector (unscaled softmax)."""
    out = {}
    for h in ("erythema", "edema", "exudate"):
        p = np.asarray(probs[h], dtype=float)
        hp = params["heads"][h]
        k = int(adjusted_pred(p[None, :], np.asarray(hp["prior"]), hp["alpha"])[0])
        value = HEADS[h]["classes"][k] if h == "exudate" else ("present" if k == 1 else "absent")
        out[h] = {"value": value, "uncertain": bool(p.max() < hp["tau"]), "confidence": float(p.max())}
    pe = float(np.asarray(probs["infection"])[1])
    band = "high concern" if pe >= params["t_flag"] else ("uncertain" if pe >= params["t_review"] else "low concern")
    out["infection"] = {"band": band, "observed_rate": band_rates[band]["rate"]}
    return out
