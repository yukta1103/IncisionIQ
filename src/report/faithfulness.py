"""Score extracted claims against a reference.

The reference is either the attribute JSON a report was generated from
(faithfulness: did the report say only what its source says?) or the
SurgWound expert labels (correctness: is what it says true?). Every claim is
one of:
  supported     value equals the reference
  contradicted  value differs from the reference (a finding that conflicts with the reference)
  unverifiable  the reference has no value for that attribute (e.g. expert label Uncertain)
"""
import pandas as pd

from src.report.claims import Claim, claims_by_attribute

# expert label -> claim vocabulary
LABEL_VALUES = {
    "erythema": ("erythema", {"Existent": "present", "Non-existent": "absent"}),
    "edema": ("edema", {"Existent": "present", "Non-existent": "absent"}),
    "exudate": ("exudate", {"Non-existent": "none", "Serous": "non_purulent", "Sanguineous": "non_purulent",
                            "Purulent": "purulent", "Seropurulent": "purulent"}),
    "infection": ("infection_risk", {"Low": "low", "Medium": "elevated", "High": "elevated"}),
    "infection_level": ("infection_risk", {"Low": "low", "Medium": "medium", "High": "high"}),
    "healing": ("healing", {"Healed": "healed", "Not Healed": "not_healed"}),
}
SCORED_ATTRIBUTES = list(LABEL_VALUES)


def expert_reference(row) -> dict[str, str | None]:
    ref = {}
    for attr, (col, mp) in LABEL_VALUES.items():
        v = row[col]
        ref[attr] = mp.get(v) if isinstance(v, str) else None
    return ref


def score_claims(claims: list[Claim], reference: dict[str, str | None], mode: str = "expert",
                 ignore: tuple[str, ...] = ()) -> list[dict]:
    """One row per (attribute, claimed value).

    mode="expert": reference None (label Uncertain) makes a claim unverifiable.
    mode="source": the reference is what the report was generated from, so a claim
    the source does not support (attribute absent, or marked uncertain) counts as
    unsupported, i.e. unfaithful.
    """
    rows = []
    for attr, values in claims_by_attribute(claims).items():
        if attr in ignore:
            continue
        for v in sorted(values):
            ref = reference.get(attr)
            if attr not in reference or (ref is None and mode == "source"):
                status = "unsupported_attribute"
            elif ref is None:
                status = "unverifiable"
            else:
                status = "supported" if v == ref else "contradicted"
            rows.append({"attribute": attr, "value": v, "reference": ref, "status": status})
    return rows


def summarize(rows: pd.DataFrame) -> dict:
    """Claim-level rates. Faithfulness = supported / (supported + contradicted + unsupported_attribute)."""
    n = len(rows)
    c = rows.status.value_counts().to_dict()
    sup, con, uns = c.get("supported", 0), c.get("contradicted", 0), c.get("unsupported_attribute", 0)
    checkable = sup + con + uns
    return {"n_claims": n, "supported": sup, "contradicted": con, "unsupported_attribute": uns,
            "unverifiable": c.get("unverifiable", 0),
            "faithfulness": sup / checkable if checkable else float("nan"),
            "contradiction_rate": (con + uns) / checkable if checkable else float("nan")}
