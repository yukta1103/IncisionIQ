"""Template report generated only from the predicted attribute JSON.

The report states nothing the JSON does not contain: no location, closure or
healing status (not predicted), and no finding for an attribute marked
uncertain. Each sentence carries at most one claim, so the faithfulness
checker can verify it.

Attribute JSON (one image):
{
  "erythema":  {"value": "present" | "absent", "uncertain": bool},
  "edema":     {"value": "present" | "absent", "uncertain": bool},
  "exudate":   {"value": "none" | "non_purulent" | "purulent", "uncertain": bool},
  "infection": {"band": "low concern" | "uncertain" | "high concern", "observed_rate": float}
}
"""

FINDING_NAMES = {"erythema": "Redness around the wound", "edema": "Swelling"}
EXUDATE_TEXT = {"none": "no drainage is visible", "non_purulent": "clear or bloody (non-purulent) drainage may be visible",
                "purulent": "purulent drainage may be visible"}


def render(attrs: dict) -> str:
    lines = ["Automated photo assessment, not a diagnosis."]
    for key in ("erythema", "edema"):
        a = attrs[key]
        name = FINDING_NAMES[key]
        if a["uncertain"]:
            lines.append(f"{name} is uncertain from this photo.")
        elif a["value"] == "present":
            lines.append(f"{name} appears present.")
        else:
            lines.append(f"{name} is not present on this photo.")
    ex = attrs["exudate"]
    if ex["uncertain"]:
        lines.append("Drainage is uncertain from this photo.")
    else:
        lines.append(f"On the photo, {EXUDATE_TEXT[ex['value']]}.")
    lines.append("Photo-based drainage assessment is unreliable, so drainage is taken from the patient's answer.")
    inf = attrs["infection"]
    rate = round(100 * inf["observed_rate"])
    if inf["band"] == "low concern":
        lines.append(f"Infection risk appears low (low-concern band; in validation {rate}% of photos in this band had a "
                     "surgeon rating of Medium or High).")
    elif inf["band"] == "high concern":
        lines.append(f"Infection risk appears elevated (high-concern band; in validation {rate}% of photos in this band "
                     "had a surgeon rating of Medium or High).")
        lines.append("Clinician review is recommended.")
    else:
        lines.append(f"Infection risk is uncertain from this photo (in validation {rate}% of photos in this band had a "
                     "surgeon rating of Medium or High).")
        lines.append("Clinician review is recommended.")
    return " ".join(lines)


def source_reference(attrs: dict) -> dict:
    """What the report is allowed to claim, in claim vocabulary (None = no claim allowed)."""
    ref = {}
    for key in ("erythema", "edema", "exudate"):
        ref[key] = None if attrs[key]["uncertain"] else attrs[key]["value"]
    ref["infection"] = {"low concern": "low", "high concern": "elevated"}.get(attrs["infection"]["band"])
    return ref
