"""Claim extractor on free-text phrasing of the kind a VLM produces.

Run: python -m pytest tests -q
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.report.claims import claims_by_attribute, extract_claims  # noqa: E402

CASES = [
    ("There is noticeable redness around the incision.", {"erythema": {"present"}}),
    ("The surrounding skin shows no redness or swelling.", {"erythema": {"absent"}, "edema": {"absent"}}),
    ("Mild swelling is visible along the suture line, but there is no redness.",
     {"edema": {"present"}, "erythema": {"absent"}}),
    ("Yellowish discharge is seen at the lower end of the wound, suggestive of pus.", {"exudate": {"purulent"}}),
    ("A small amount of clear serous fluid is present.", {"exudate": {"non_purulent"}}),
    ("The wound appears dry with no drainage.", {"exudate": {"none"}}),
    ("There are signs of infection, including warmth and purulent discharge.",
     {"infection": {"elevated"}, "exudate": {"purulent"}}),
    ("No signs of infection are present.", {"infection": {"low"}}),
    ("Overall the infection risk appears moderate.", {"infection": {"elevated"}, "infection_level": {"medium"}}),
    ("The incision is well-healed.", {"healing": {"healed"}}),
    ("The wound has not yet healed and the edges are slightly separated.", {"healing": {"not_healed"}}),
    ("Monitor for increased redness, swelling, or discharge, which could indicate infection.", {}),
    ("Keep the area clean and dry to reduce the risk of infection.", {}),
    ("Erythema status is uncertain from this photo.", {}),
    ("Erythema and edema are both absent.", {"erythema": {"absent"}, "edema": {"absent"}}),
    ("Redness around the wound is not present on this photo.", {"erythema": {"absent"}}),
    ("Redness around the incision is uncertain from this photo.", {}),
    ("Some non-purulent drainage may be visible.", {"exudate": {"non_purulent"}}),
    ("Infection risk appears elevated.", {"infection": {"elevated"}}),
    ("Swelling along the suture line is absent.", {"edema": {"absent"}}),
]


@pytest.mark.parametrize("text,expected", CASES)
def test_claims(text, expected):
    got = claims_by_attribute(extract_claims(text))
    for attr, values in expected.items():
        assert got.get(attr) == values, (text, attr, got)
    assert set(got) - set(expected) - {"infection_level"} == set(), (text, got)
