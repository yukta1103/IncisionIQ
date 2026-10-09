# Phase 5 tables

## 1. Claim extractor validated on the SurgWound expert reports

Agreement of claims extracted from each expert report with that image's expert label. The rules were tuned while inspecting failures on all splits, so this is a sanity check of the extractor, not a held-out estimate; free-text phrasing is covered by unit tests (`tests/test_claims.py`).

| attribute   | split   |   n |   claim_made |   agrees_with_label |   conflicting_value |
|:------------|:--------|----:|-------------:|--------------------:|--------------------:|
| edema       | test    | 115 |        0.983 |            0.947826 |          0.0347826  |
| edema       | train   | 378 |        0.987 |            0.970899 |          0.015873   |
| edema       | val     |  61 |        0.984 |            0.967213 |          0.0327869  |
| erythema    | test    | 131 |        0.985 |            0.954198 |          0.0305344  |
| erythema    | train   | 463 |        0.985 |            0.963283 |          0.0215983  |
| erythema    | val     |  66 |        0.985 |            0.954545 |          0.030303   |
| exudate     | test    | 125 |        0.96  |            0.96     |          0          |
| exudate     | train   | 437 |        0.963 |            0.95881  |          0.00457666 |
| exudate     | val     |  64 |        0.984 |            0.984375 |          0          |
| healing     | test    | 137 |        0.927 |            0.927007 |          0          |
| healing     | train   | 480 |        0.956 |            0.95625  |          0          |
| healing     | val     |  69 |        0.87  |            0.869565 |          0          |
| infection   | test    | 137 |        0.993 |            0.970803 |          0.0291971  |
| infection   | train   | 480 |        0.969 |            0.96875  |          0.00208333 |
| infection   | val     |  69 |        0.957 |            0.956522 |          0          |

Expert reports also state a value for attributes whose label is Uncertain (the question row is missing). Those claims are scored as unverifiable:

| attribute   |   n_uncertain_label |   report_states_value |
|:------------|--------------------:|----------------------:|
| edema       |                 132 |                 0.364 |
| erythema    |                  26 |                 0.731 |
| exudate     |                  60 |                 0.217 |

## 2. Template reports: faithfulness and correctness

Faithfulness = share of checkable claims that match the attribute JSON the report was generated from. Correctness = share of claims on labeled attributes that match the expert label. Contradiction = claims that conflict with the reference.

| subset | n images | claims per report | faithfulness to source | correctness vs expert labels | contradicts expert labels |
|---|---|---|---|---|---|
| all | 686 | 3.1 [3.1, 3.2] | 1.000 [1.000, 1.000] | 0.81 [0.79, 0.83] | 0.19 [0.17, 0.21] |
| excl_900plus | 613 | 3.2 [3.1, 3.2] | 1.000 [1.000, 1.000] | 0.82 [0.80, 0.85] | 0.18 [0.15, 0.20] |
| official_test | 137 | 3.1 [3.0, 3.3] | 1.000 [1.000, 1.000] | 0.81 [0.76, 0.86] | 0.19 [0.14, 0.24] |

Reference point: the SurgWound expert reports themselves, scored by the same checker against their own labels (this measures checker plus report-label agreement, an upper bound for any report):

| subset | claims per report | correctness vs expert labels |
|---|---|---|
| all | 5.6 [5.5, 5.6] | 0.99 [0.99, 0.99] |
| excl_900plus | 5.6 [5.5, 5.7] | 0.99 [0.99, 0.99] |
| official_test | 5.6 [5.5, 5.8] | 0.98 [0.97, 0.99] |

Template correctness by attribute (all images; claims on labeled attributes):

| attribute       |   claims |   correct |
|:----------------|---------:|----------:|
| edema           |      452 |     0.836 |
| erythema        |      506 |     0.739 |
| exudate         |      488 |     0.922 |
| infection       |      529 |     0.673 |
| infection_level |      287 |     0.958 |

Share of reports stating 'uncertain' instead of a finding: erythema 0.24, edema 0.18, exudate 0.22; infection bands: {'low concern': 287, 'high concern': 242, 'uncertain': 157}.

## 3. Examples (official test split)

**471.jpg** (expert: erythema Non-existent, edema Non-existent, exudate Non-existent, infection risk Low)

> Automated photo assessment, not a diagnosis. Redness around the wound is not present on this photo. Swelling is not present on this photo. On the photo, no drainage is visible. Photo-based drainage assessment is unreliable, so drainage is taken from the patient's answer. Infection risk appears low (low-concern band; in validation 4% of photos in this band had a surgeon rating of Medium or High).

**146.jpg** (expert: erythema Existent, edema Non-existent, exudate Sanguineous, infection risk Medium)

> Automated photo assessment, not a diagnosis. Redness around the wound appears present. Swelling is uncertain from this photo. Drainage is uncertain from this photo. Photo-based drainage assessment is unreliable, so drainage is taken from the patient's answer. Infection risk appears elevated (high-concern band; in validation 33% of photos in this band had a surgeon rating of Medium or High). Clinician review is recommended.

**659.jpg** (expert: erythema Non-existent, edema Non-existent, exudate Non-existent, infection risk Low)

> Automated photo assessment, not a diagnosis. Redness around the wound is not present on this photo. Swelling is not present on this photo. On the photo, no drainage is visible. Photo-based drainage assessment is unreliable, so drainage is taken from the patient's answer. Infection risk is uncertain from this photo (in validation 13% of photos in this band had a surgeon rating of Medium or High). Clinician review is recommended.

**734.jpg** (expert: erythema Non-existent, edema None, exudate Non-existent, infection risk Low)

> Automated photo assessment, not a diagnosis. Redness around the wound is uncertain from this photo. Swelling is not present on this photo. On the photo, no drainage is visible. Photo-based drainage assessment is unreliable, so drainage is taken from the patient's answer. Infection risk appears low (low-concern band; in validation 4% of photos in this band had a surgeon rating of Medium or High).

