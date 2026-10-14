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
    # found by running the checker on the expert reports through the full VLM scoring path
    ("The wound is currently devoid of exudate, erythema, and edema.",
     {"exudate": {"none"}, "erythema": {"absent"}, "edema": {"absent"}}),
    ("The wound shows absence of exudate and erythema, and presence of edema.",
     {"exudate": {"none"}, "erythema": {"absent"}, "edema": {"present"}}),
    ("There is sanguineous exudate with no evident erythema or edema present.",
     {"exudate": {"non_purulent"}, "erythema": {"absent"}, "edema": {"absent"}}),
    ("The wound is not healed, displaying purulent exudate.", {"healing": {"not_healed"}, "exudate": {"purulent"}}),
    ("There is an absence of significant signs of infection.", {"infection": {"low"}}),
    ("The wound is deemed low risk for infection.", {"infection": {"low"}, "infection_level": {"low"}}),
    ("The edges are well approximated, with no visible gaping or dehiscence.", {}),
]

MARKDOWN = """# Surgical Wound Assessment Report
### 2. Wound Status
- The incision appears closed, with no visible gaping or dehiscence.
- The line is pink, suggesting early healing (proliferative phase).
### 4. Exudate Characteristics
- **Amount:** None visible
- **Type:** No serous, sanguineous, or purulent drainage
### 5. Erythema
- **Minimal, confined to the incision line.**
### 6. Edema
- **No significant edema is apparent.**
### 7. Urgency Level
- **Escalate** if any of the following occur:
  - Purulent or foul-smelling discharge.
  - Spreading redness or swelling.
### 8. Infection Risk Assessment
**Risk level: Moderate.**
| Factor | Observation |
|---|---|
| Spreading erythema/cellulitis | Absent |
### Recommendations
- Watch for purulent discharge or fever.
"""


def test_markdown_claims():
    from src.report.markdown_claims import extract_markdown_claims

    got = claims_by_attribute(extract_markdown_claims(MARKDOWN))
    assert got == {"healing": {"not_healed"}, "exudate": {"none"}, "erythema": {"present"}, "edema": {"absent"},
                   "infection": {"elevated"}, "infection_level": {"medium"}}, got


@pytest.mark.parametrize("text,expected", CASES)
def test_claims(text, expected):
    got = claims_by_attribute(extract_claims(text))
    for attr, values in expected.items():
        assert got.get(attr) == values, (text, attr, got)
    assert set(got) - set(expected) - {"infection_level"} == set(), (text, got)
