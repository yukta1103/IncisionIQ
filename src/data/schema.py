"""Attribute schema for SurgWound (Xu et al., npj Digital Medicine 2026)."""

SPLITS = ["train", "val", "test"]

# Raw field name in the HF JSON -> short column name used everywhere else.
FIELD_TO_COL = {
    "Wound Location": "location",
    "Healing Status": "healing",
    "Closure Method": "closure",
    "Exudate Type": "exudate",
    "Erythema": "erythema",
    "Edema": "edema",
    "Infection Risk Assessment": "infection_risk",
    "Urgency Level": "urgency",
}
ATTRS = list(FIELD_TO_COL.values())

# Long urgency strings are shortened to keep tables readable.
URGENCY_SHORT = {
    "Home Care (Green): Manage with routine care": "Home Care",
    "Clinic Visit (Yellow): Requires professional evaluation within 48 hours": "Clinic Visit",
    "Emergency Care (Red): Seek immediate medical attention": "Emergency Care",
}

UNCERTAIN = "Uncertain"
