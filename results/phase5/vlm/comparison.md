# Phase 5: VLM baseline vs grounded template reports

All report sets are scored by the same claim checker against the SurgWound expert labels.

- **Correctness** = supported / (supported + contradicted). **Primary: refusals and failed requests counted as incorrect** (every expert-labeled attribute of that image counts as an incorrect claim). Secondary: excluded.
- **Hallucination rate** = contradicted claims / all extracted claims, on produced reports only.
- **Unverifiable** = claims on attributes whose expert label is Uncertain.
- Condition A (markdown reports) is read with the section-aware extractor (`src/report/markdown_claims.py`); template and condition B with the prose extractor. Condition A's checker was validated against hand labels on 30 random reports; headline comparisons use only the attributes where it agrees at 0.96 or above (erythema, edema, infection).

### Checker validation on condition A (30 hand-labeled reports)

| extractor | attribute | n | agreement | wrong value | missed |
|---|---|---|---|---|---|
| markdown | edema | 26 | 0.96 | 0.00 | 0.04 |
| markdown | erythema | 29 | 0.97 | 0.00 | 0.03 |
| markdown | exudate | 30 | 0.73 | 0.17 | 0.10 |
| markdown | healing | 25 | 0.76 | 0.16 | 0.08 |
| markdown | infection | 30 | 0.97 | 0.00 | 0.03 |
| prose | edema | 26 | 0.08 | 0.92 | 0.00 |
| prose | erythema | 29 | 0.21 | 0.79 | 0.00 |
| prose | exudate | 30 | 0.17 | 0.83 | 0.00 |
| prose | healing | 25 | 0.48 | 0.20 | 0.32 |
| prose | infection | 30 | 0.43 | 0.50 | 0.07 |
| markdown | all | 140 | 0.88 | 0.06 | 0.06 |
| prose | all | 140 | 0.27 | 0.66 | 0.07 |

## Refusals and failed requests (run 1)

| condition | refused | failed | ok |
|---|---|---|---|
| vlm_A | 0 | 0 | 686 |
| vlm_B | 0 | 0 | 686 |

Refusals by expert infection risk and exudate class (all 686 images, run 1):

| condition | label | class | n images | refused | refused share |
|---|---|---|---|---|---|
| vlm_A | infection_risk | Low | 573 | 0 | 0.000 |
| vlm_A | infection_risk | Medium | 90 | 0 | 0.000 |
| vlm_A | infection_risk | High | 23 | 0 | 0.000 |
| vlm_A | exudate | Non-existent | 531 | 0 | 0.000 |
| vlm_A | exudate | Serous | 36 | 0 | 0.000 |
| vlm_A | exudate | Sanguineous | 29 | 0 | 0.000 |
| vlm_A | exudate | Purulent | 19 | 0 | 0.000 |
| vlm_A | exudate | Seropurulent | 11 | 0 | 0.000 |
| vlm_A | exudate | Uncertain | 60 | 0 | 0.000 |
| vlm_B | infection_risk | Low | 573 | 0 | 0.000 |
| vlm_B | infection_risk | Medium | 90 | 0 | 0.000 |
| vlm_B | infection_risk | High | 23 | 0 | 0.000 |
| vlm_B | exudate | Non-existent | 531 | 0 | 0.000 |
| vlm_B | exudate | Serous | 36 | 0 | 0.000 |
| vlm_B | exudate | Sanguineous | 29 | 0 | 0.000 |
| vlm_B | exudate | Purulent | 19 | 0 | 0.000 |
| vlm_B | exudate | Seropurulent | 11 | 0 | 0.000 |
| vlm_B | exudate | Uncertain | 60 | 0 | 0.000 |

## Headline: claims on erythema, edema and infection only (checker validated on all three sets)

| subset | report set | n images | claims per report | correctness (primary: refusals incorrect) | hallucination rate | reports with a contradiction |
|---|---|---|---|---|---|---|
| excl_900plus | template | 613 | 2.4 [2.3, 2.4] | 0.76 [0.73, 0.79] | 0.22 [0.19, 0.25] | 0.40 [0.36, 0.44] |
| excl_900plus | vlm_A | 613 | 3.0 [2.9, 3.0] | 0.62 [0.60, 0.64] | 0.35 [0.33, 0.37] | 0.73 [0.70, 0.77] |
| excl_900plus | vlm_B | 613 | 3.0 [3.0, 3.0] | 0.69 [0.66, 0.72] | 0.29 [0.26, 0.31] | 0.54 [0.50, 0.58] |
| all | template | 686 | 2.4 [2.3, 2.4] | 0.75 [0.72, 0.77] | 0.23 [0.21, 0.26] | 0.42 [0.38, 0.45] |
| all | vlm_A | 686 | 3.0 [2.9, 3.0] | 0.61 [0.58, 0.63] | 0.37 [0.34, 0.39] | 0.75 [0.71, 0.78] |
| all | vlm_B | 686 | 3.0 [3.0, 3.0] | 0.68 [0.65, 0.70] | 0.30 [0.27, 0.32] | 0.55 [0.51, 0.59] |
| official_test | template | 137 | 2.4 [2.3, 2.5] | 0.75 [0.69, 0.80] | 0.23 [0.18, 0.29] | 0.42 [0.33, 0.50] |
| official_test | vlm_A | 137 | 3.0 [3.0, 3.0] | 0.57 [0.53, 0.62] | 0.40 [0.36, 0.44] | 0.82 [0.76, 0.89] |
| official_test | vlm_B | 137 | 3.0 [3.0, 3.0] | 0.61 [0.55, 0.67] | 0.36 [0.30, 0.42] | 0.64 [0.55, 0.72] |

Paired differences vs template, validated attributes (same group resamples):

| subset | comparison | correctness diff (primary) | hallucination rate diff |
|---|---|---|---|
| excl_900plus | vlm_A minus template | -0.14 [-0.18, -0.11] | +0.13 [+0.10, +0.17] |
| excl_900plus | vlm_B minus template | -0.07 [-0.10, -0.04] | +0.07 [+0.04, +0.10] |
| all | vlm_A minus template | -0.14 [-0.17, -0.11] | +0.13 [+0.10, +0.16] |
| all | vlm_B minus template | -0.07 [-0.10, -0.03] | +0.06 [+0.03, +0.09] |
| official_test | vlm_A minus template | -0.17 [-0.24, -0.11] | +0.17 [+0.10, +0.23] |
| official_test | vlm_B minus template | -0.14 [-0.21, -0.06] | +0.13 [+0.06, +0.19] |

## All attributes (exudate and healing included; condition A checker agreement there is 0.73 and 0.76)

| subset | report set | n images | reports produced | claims per report | correctness (primary: refusals incorrect) | correctness (refusals excluded) | hallucination rate | reports with a contradiction | unverifiable share |
|---|---|---|---|---|---|---|---|---|---|
| excl_900plus | template | 613 | 613 | 3.6 [3.5, 3.7] | 0.82 [0.80, 0.85] | 0.82 [0.80, 0.85] | 0.16 [0.14, 0.19] | 0.42 [0.38, 0.46] | 0.07 [0.05, 0.08] |
| excl_900plus | vlm_A | 613 | 613 | 5.9 [5.8, 5.9] | 0.62 [0.60, 0.64] | 0.62 [0.60, 0.64] | 0.36 [0.34, 0.38] | 0.90 [0.87, 0.92] | 0.05 [0.04, 0.06] |
| excl_900plus | vlm_B | 613 | 613 | 4.7 [4.7, 4.8] | 0.76 [0.73, 0.78] | 0.76 [0.73, 0.78] | 0.23 [0.21, 0.25] | 0.58 [0.54, 0.63] | 0.06 [0.05, 0.08] |
| all | template | 686 | 686 | 3.5 [3.4, 3.6] | 0.81 [0.79, 0.83] | 0.81 [0.79, 0.83] | 0.18 [0.16, 0.20] | 0.44 [0.40, 0.48] | 0.07 [0.06, 0.08] |
| all | vlm_A | 686 | 686 | 5.9 [5.8, 5.9] | 0.61 [0.60, 0.63] | 0.61 [0.60, 0.63] | 0.37 [0.35, 0.38] | 0.90 [0.87, 0.92] | 0.05 [0.04, 0.06] |
| all | vlm_B | 686 | 686 | 4.7 [4.7, 4.7] | 0.74 [0.72, 0.77] | 0.74 [0.72, 0.77] | 0.24 [0.22, 0.26] | 0.60 [0.56, 0.64] | 0.07 [0.06, 0.08] |
| official_test | template | 137 | 137 | 3.6 [3.4, 3.8] | 0.81 [0.76, 0.86] | 0.81 [0.76, 0.86] | 0.17 [0.13, 0.22] | 0.43 [0.35, 0.52] | 0.08 [0.05, 0.11] |
| official_test | vlm_A | 137 | 137 | 6.0 [5.9, 6.0] | 0.58 [0.54, 0.61] | 0.58 [0.54, 0.61] | 0.40 [0.37, 0.44] | 0.93 [0.88, 0.97] | 0.05 [0.03, 0.07] |
| official_test | vlm_B | 137 | 137 | 4.6 [4.5, 4.7] | 0.70 [0.64, 0.75] | 0.70 [0.64, 0.75] | 0.29 [0.24, 0.34] | 0.67 [0.59, 0.75] | 0.06 [0.04, 0.09] |

Paired differences vs template on the same group resamples (correctness primary; hallucination rate on images where the VLM produced a report):

| subset | comparison | correctness diff (primary) | hallucination rate diff |
|---|---|---|---|
| excl_900plus | vlm_A minus template | -0.20 [-0.23, -0.17] | +0.19 [+0.17, +0.22] |
| excl_900plus | vlm_B minus template | -0.07 [-0.09, -0.04] | +0.06 [+0.04, +0.09] |
| all | vlm_A minus template | -0.20 [-0.22, -0.17] | +0.19 [+0.17, +0.21] |
| all | vlm_B minus template | -0.07 [-0.09, -0.04] | +0.06 [+0.04, +0.09] |
| official_test | vlm_A minus template | -0.24 [-0.29, -0.18] | +0.23 [+0.18, +0.28] |
| official_test | vlm_B minus template | -0.12 [-0.17, -0.06] | +0.11 [+0.06, +0.16] |

### Correctness by attribute (excluding ID 900+, produced reports)

| attribute | template claims | template correct | vlm_A claims | vlm_A correct | vlm_B claims | vlm_B correct |
|---|---|---|---|---|---|---|
| erythema | 458 | 0.74 | 585 | 0.44 | 591 | 0.62 |
| edema | 410 | 0.86 | 486 | 0.55 | 497 | 0.69 |
| exudate | 456 | 0.92 | 552 | 0.51 | 565 | 0.82 |
| infection | 463 | 0.69 | 609 | 0.85 | 613 | 0.76 |
| infection_level | 277 | 0.96 | 594 | 0.84 | 439 | 0.93 |
| healing | 0 | n/a | 599 | 0.52 | 0 | n/a |

## Condition B as a zero-shot classifier vs model A (excluding ID 900+)

Primary: a refused or failed VLM request counts as a missed finding (negative class; for infection, a missed Elevated case). Model A uses its tuned decision rule; for infection it is the flag (high-concern band). Hard decisions, group-bootstrap CIs, paired difference on the same images.

| head | n | macro F1 VLM-B (primary) | macro F1 VLM-B (refusals excluded) | macro F1 model A | diff VLM-B minus A (primary) | critical recall VLM-B | critical recall model A |
|---|---|---|---|---|---|---|---|
| erythema | 591 | 0.61 [0.57, 0.64] | 0.61 [0.57, 0.64] | 0.61 [0.57, 0.66] | -0.01 [-0.06, +0.04] | 0.83 [0.77, 0.89] | 0.50 [0.43, 0.58] |
| edema | 497 | 0.59 [0.54, 0.64] | 0.59 [0.54, 0.64] | 0.65 [0.59, 0.71] | -0.06 [-0.12, -0.00] | 0.68 [0.55, 0.79] | 0.53 [0.38, 0.66] |
| exudate | 565 | 0.62 [0.55, 0.69] | 0.62 [0.55, 0.69] | 0.48 [0.41, 0.54] | +0.15 [+0.05, +0.24] | 0.69 [0.52, 0.86] | 0.10 [0.00, 0.22] |
| infection | 613 | 0.64 [0.59, 0.68] | 0.64 [0.59, 0.68] | 0.62 [0.57, 0.66] | +0.02 [-0.03, +0.07] | 0.65 [0.54, 0.77] | 0.64 [0.54, 0.75] |

### Infection: Elevated recall and false alarms per 100 at each system's decision (excluding ID 900+)

The VLM gives a single label with no score, so its decision **cannot be threshold-tuned**; it is compared at its native decision. Model A is shown at the chosen operating point (flag, and flag or refer).

| system | Elevated recall | High-risk caught | false alarms per 100 | flagged per 100 |
|---|---|---|---|---|
| VLM-B native decision (refusals = missed, primary) | 0.65 [0.54, 0.77] | 0.92 [0.73, 1.00] (n=12) | 19.4 [16.1, 22.7] | 28.4 [24.2, 32.5] |
| model A, flag (high-concern band) | 0.64 [0.54, 0.75] | 0.67 [0.36, 0.92] (n=12) | 21.5 [17.9, 25.2] | 30.3 [26.1, 34.4] |
| model A, flag or refer (high-concern or uncertain band) | 0.86 [0.78, 0.93] | 0.83 [0.58, 1.00] (n=12) | 43.1 [38.9, 47.0] | 54.8 [50.3, 58.9] |

VLM-B with refusals excluded (n = 613): Elevated recall 0.65, false alarms per 100 19.4.

## Run-to-run variation

Not measured. The two repeat runs on the official test split were dropped to keep the batch under the $15 budget (projected $20.64 for the full plan at effort low, $14.75 without repeats).

## Examples: condition A contradicting the expert labels

Drawn at random from contradicted claims on the validated attributes (erythema, edema, infection), at most three per attribute, so each example reflects the report text rather than a checker error. Clauses phrased as "minimal or none" / "mild to none" are skipped here (they were labeled unclear in the checker validation); they still count in the scores.

- **274.jpg**: erythema claimed **present**, expert label **absent**. Model text: "Present, localized. A pink-to-red halo surrounds the central purple lesion, extending a few millimeters to about 1 cm." (expert labels: erythema absent, edema absent, exudate none, infection low)
- **449.jpg**: erythema claimed **present**, expert label **absent**. Model text: "Present, mild, and localized to the upper portion of the incision." (expert labels: erythema absent, edema absent, exudate none, infection low)
- **707.jpg**: infection claimed **elevated**, expert label **low**. Model text: "Overall risk: moderate." (expert labels: erythema absent, edema absent, exudate none, infection low)
- **119.jpg**: erythema claimed **absent**, expert label **present**. Model text: "Assessment: No significant spreading redness is evident." (expert labels: erythema present, edema present, exudate none, infection low)
- **146.jpg**: infection claimed **low**, expert label **elevated**. Model text: "Overall risk: LOW." (expert labels: erythema present, edema absent, exudate non_purulent, infection elevated)
- **186.jpg**: edema claimed **present**, expert label **absent**. Model text: "Present: Mild to moderate, likely." (expert labels: erythema absent, edema absent, exudate none, infection low)
- **654.jpg**: infection claimed **elevated**, expert label **low**. Model text: "Risk level: Moderate to high. This may be a superficial surgical site infection (CDC criteria: superficial incisional SSI)." (expert labels: erythema present, edema None, exudate none, infection low)
- **984.jpg** (ID 900+): edema claimed **present**, expert label **absent**. Model text: "Mild to moderate swelling appears present in the lower leg, ankle, and foot." (expert labels: erythema absent, edema absent, exudate none, infection low)
