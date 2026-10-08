"""Head definitions approved after Phase 1.

Missing attributes (which mean "Uncertain" in SurgWound) map to -1 and are
masked out of the loss and the metrics.
"""
import numpy as np
import pandas as pd

HEADS = {
    "erythema": {"classes": ["none", "present"],
                 "map": {"Non-existent": 0, "Existent": 1}},
    "edema": {"classes": ["none", "present"],
              "map": {"Non-existent": 0, "Existent": 1}},
    "exudate": {"classes": ["none", "non_purulent", "purulent"],
                "map": {"Non-existent": 0, "Serous": 1, "Sanguineous": 1,
                        "Purulent": 2, "Seropurulent": 2}},
    "infection": {"classes": ["low", "elevated"], "source": "infection_risk",
                  "map": {"Low": 0, "Medium": 1, "High": 1}},
}
HEAD_NAMES = list(HEADS)
# Class whose recall is reported separately (the clinically important one).
CRITICAL_CLASS = {"erythema": 1, "edema": 1, "exudate": 2, "infection": 1}


def encode_labels(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({"image_name": df.image_name})
    for h, spec in HEADS.items():
        src = df[spec.get("source", h)]
        out[h] = src.map(spec["map"]).fillna(-1).astype(int)
    out["infection_high"] = (df.infection_risk == "High").astype(int)
    out["image_id"] = df.image_name.str.extract(r"(\d+)")[0].astype(int)
    out["source_900plus"] = (out.image_id >= 900).astype(int)
    return out


def label_matrix(lab: pd.DataFrame) -> np.ndarray:
    return lab[HEAD_NAMES].to_numpy()
