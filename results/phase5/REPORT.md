# Phase 5: Grounded report generation and faithfulness check

Reproduce (all paths relative to the repo root):
```
python scripts/phase5_reports.py              # template reports, checker validation on expert reports
python scripts/phase5_vlm.py prepare          # VLM inputs (no API calls)
python scripts/phase5_vlm.py pilot            # 4 requests, cost projection (API, about $0.10)
python scripts/phase5_vlm.py submit --runs run1
python scripts/phase5_vlm.py collect          # download, map back locally, delete the batch
python scripts/phase5_markdown_validation.py  # checker vs hand labels on 30 condition A reports
python scripts/phase5_checker_errors.py       # direction of remaining checker errors, spot-check export
python scripts/phase5_compare.py              # all comparisons below
```
Tables: `tables.md` (template, checker validation on expert reports), `vlm/comparison.md` (VLM comparison), `markdown_validation.json` and `markdown_validation_labels.csv` (hand-label validation), `checker_error_direction.json`, `contradiction_review.csv` (manual review of 38 contradictions). **Spot-check file: `markdown_validation_export.md`** (the 30 validation reports in full, with hand labels, checker output and surgeon labels). Raw VLM outputs keyed by image name: `vlm/vlm_outputs.parquet`.

## Headline

- **Grounded generation beats free generation from the same model.** VLM condition A (free-text report) and condition B (the same model's structured answer, rendered by our template) see the same image with the same model; only the generation step differs. On erythema, edema and infection risk, excluding ID 900+ (n = 613), B's claims agree with the surgeon labels 0.69 [0.66, 0.72] of the time and A's 0.62 [0.60, 0.64]. **This A vs B gap is the generation effect and is the primary evidence for grounded reports.**
- **Our template beats VLM B (0.76 [0.73, 0.79] vs 0.69, paired difference -0.07 [-0.10, -0.04]), but that gap is largely supervised vs zero-shot:** model A was trained on these annotators' labels and learned their grading thresholds, while the VLM never saw them.
- **Claims contradicting surgeon labels** (share of all claims), same attributes: template 0.22 [0.19, 0.25], VLM B 0.29 [0.26, 0.31], VLM A 0.35 [0.33, 0.37].
- **These contradictions are mostly not hallucinations.** In a manual review of 38 condition A contradictions against the images, 25 were threshold disagreements (mild, visible findings called present that the surgeons graded absent), 7 risk-level judgment calls, 2 missed findings, 4 checker errors, and **0 hallucinations** (a finding asserted that is clearly absent from the photo).
- **Perception is competitive.** Zero-shot VLM B ties our model on infection risk at a similar alert rate, catches 11 of 12 High-risk wounds against our 8, and is better on exudate (see the section below).
- **No refusals** (0 of 1,372 requests), so the primary scoring (refusals counted as incorrect) equals the secondary (refusals excluded).

## Setup

**Template reports (ours).** Rendered only from model A's out-of-fold attribute JSON (`src/report/template.py`): erythema, edema, exudate (stated as unreliable, drainage comes from the patient), and infection risk as its Phase 4 band with the band's observed rate. Attributes in the "uncertain" abstention zone are stated as uncertain and make no claim. No location, closure or healing status is stated, since the model does not predict them.

**VLM baseline.** Claude Opus 5.5 (`claude-opus-5-5`) via the Message Batches API, zero-shot, one run per image (686 images x 2 conditions = 1,372 requests).
- **Condition A, free text:** the SurgWound report-task instruction, verbatim.
- **Condition B, structured:** a JSON schema restricted to exactly our label options (erythema none/present, edema none/present, exudate none/non_purulent/purulent, infection risk low/elevated), rendered by our template generator. B differs from the template only in where the attributes come from, and from A only in how the report is generated.
- **Both conditions ran at effort `low`, with identical settings, because of budget.** The full plan at the default effort projected $28.74 and at `low` $20.64; the two repeat runs on the official test split were then dropped to stay under the $15 cap (projection $14.75). Higher effort might strengthen the VLM baseline, and run-to-run variation was not measured.
- Actual cost: **$15.58** for the batch (1,375,196 input and 1,282,962 output tokens at batch prices), plus about $0.22 for two 4-request pilots. The 2-sample projection underestimated slightly.
- **Data handling:** only inpainted images were sent (text, account numbers and redaction boxes removed), re-encoded from raw pixels (no EXIF or other metadata), long side at most 1024 px, inline base64, with random opaque request IDs. No file names, labels or IDs were sent. The batch was deleted after download. Anthropic terms and links: README.

**Scoring.** Every report is reduced to claims (attribute, value) and each claim is compared with the SurgWound surgeon label: supported, contradicted, or unverifiable (label Uncertain). Correctness = supported / (supported + contradicted). Primary: refusals and failed requests count as incorrect for every labeled attribute of that image (none occurred). Group-bootstrap 95% CIs (patient groups), paired differences on the same resamples. Primary subset excludes ID 900+.

## The claim checker

**The checker for condition A was redesigned after inspecting the VLM's outputs, because of documented checker errors.** The prose extractor (`src/report/claims.py`) agrees with the surgeon labels on 87 to 98% of attributes when run on SurgWound's own expert reports (`tables.md`), and the template's faithfulness to its own JSON is 1.000. Condition A's reports are different: about 4,500 characters of markdown with one section per requested aspect, tables, and lists of warning signs ("seek care if: purulent discharge, spreading redness"). Run over whole reports, the prose extractor read headings ("### Erythema") and warning-sign lists as findings; in a hand review of 15 of its contradictions, 8 were checker errors.

The redesigned, section-aware extractor (`src/report/markdown_claims.py`) reads each attribute only from its own section, up to the first escalation or advice list, and ignores headings, tables and recommendation sections. It was developed on separate reports, frozen, and validated once against hand labels on 30 random condition A reports. The labels were written from the report text before seeing the extractor's output; 10 of 150 judgments were genuinely ambiguous and were excluded.

| attribute | n | agreement, section-aware | agreement, prose extractor |
|---|---|---|---|
| erythema | 29 | 0.97 | 0.21 |
| edema | 26 | 0.96 | 0.08 |
| infection risk | 30 | 0.97 | 0.43 |
| exudate | 30 | 0.73 | 0.17 |
| healing status | 25 | 0.76 | 0.48 |
| all | 140 | 0.88 | 0.27 |

**Direction of the remaining errors** (same 30 reports, scored against the surgeon labels with the hand label vs the checker's extraction; surgeon-Uncertain and hand-unclear items excluded):

| report set | attribute | correct | false contradictions | missed contradictions | other |
|---|---|---|---|---|---|
| VLM A | erythema | 28 | 0 | 1 | 0 |
| VLM A | edema | 23 | 0 | 1 | 0 |
| VLM A | infection risk | 29 | 0 | 1 | 0 |
| VLM A | exudate | 20 | 4 | 2 | 1 |
| VLM A | healing status | 19 | 3 | 2 | 1 |
| VLM A | all | 119 | 7 | 7 | 2 |
| template, VLM B | all | rendered by our template; checker faithfulness to the source JSON is 1.000, so no extraction errors | | | |

On the three headline attributes the validation sample shows no false contradictions, only misses (the checker slightly under-counts condition A's contradictions there). The separate review of 38 contradictions (below) found 4 checker-made contradictions on the same attributes, mostly "minimal to none" phrasing read as present. So condition A's headline contradiction rate contains a small number of false contradictions and misses a similar number; the two partly cancel. Headline comparisons use erythema, edema and infection only; exudate and healing results for condition A carry the lower agreement. A known gap: about 1% of condition A reports use bold-text headings instead of markdown headings and yield no claims. The extractor was not changed after validation.

## Results

### Headline: erythema, edema, infection risk

| subset | report set | n | claims per report | correctness | claims contradicting surgeon labels | reports with a contradiction |
|---|---|---|---|---|---|---|
| excl. 900+ | template | 613 | 2.4 | **0.76 [0.73, 0.79]** | 0.22 [0.19, 0.25] | 0.40 [0.36, 0.44] |
| excl. 900+ | VLM B | 613 | 3.0 | **0.69 [0.66, 0.72]** | 0.29 [0.26, 0.31] | 0.54 [0.50, 0.58] |
| excl. 900+ | VLM A | 613 | 3.0 | **0.62 [0.60, 0.64]** | 0.35 [0.33, 0.37] | 0.73 [0.70, 0.77] |
| all | template | 686 | 2.4 | 0.75 [0.72, 0.77] | 0.23 [0.21, 0.26] | 0.42 [0.38, 0.45] |
| all | VLM B | 686 | 3.0 | 0.68 [0.65, 0.70] | 0.30 [0.27, 0.32] | 0.55 [0.51, 0.59] |
| all | VLM A | 686 | 3.0 | 0.61 [0.58, 0.63] | 0.37 [0.34, 0.39] | 0.75 [0.71, 0.78] |
| official test | template | 137 | 2.4 | 0.75 [0.69, 0.80] | 0.23 [0.18, 0.29] | 0.42 [0.33, 0.50] |
| official test | VLM B | 137 | 3.0 | 0.61 [0.55, 0.67] | 0.36 [0.30, 0.42] | 0.64 [0.55, 0.72] |
| official test | VLM A | 137 | 3.0 | 0.57 [0.53, 0.62] | 0.40 [0.36, 0.44] | 0.82 [0.76, 0.89] |

Paired differences against the template (excl. 900+): VLM A correctness -0.14 [-0.18, -0.11], contradicting claims +0.13 [+0.10, +0.17]; VLM B correctness -0.07 [-0.10, -0.04], contradicting claims +0.07 [+0.04, +0.10]. The template makes fewer claims because uncertain predictions are stated as uncertain; that abstention is part of why its claims are more often right.

### What the gaps mean

- **A vs B: the generation effect (primary evidence for grounded reports).** Same model, same image, same moment. Asked to write freely, the model's statements disagree with the surgeons more often (0.62 vs 0.69 correct, 0.35 vs 0.29 contradicting); asked for the attributes and passed through our grounded template, they agree more. Free text also states more (5.9 vs 4.7 claims per report on all scored attributes, plus location, closure and urgency, which are not scored), and 73% of free-text reports contain at least one contradiction on the headline attributes, against 54% for the templated version. This is the cleanest evidence in the project that constraining generation to explicit attributes reduces wrong statements.
- **Template vs B: mostly supervised vs zero-shot.** Model A was trained on these annotators' labels, so it learned where they draw the line (for example, that faint pinkness along a healing incision counts as no erythema). The VLM applies its own threshold, and most of its contradictions are exactly that kind of disagreement (next section). The template's advantage over B is therefore not evidence that our model perceives wounds better.

### Contradictions: threshold disagreements vs hallucinations

The 8 published examples plus 30 further contradictions drawn at random (condition A, headline attributes) were reviewed against the images the VLM received (`contradiction_review.csv`). A **hallucination** here means the report asserts a finding that is clearly absent from the photo. Judgments are from photographs by a non-clinician, so borderline cases were counted as threshold disagreements, not hallucinations.

| category | published 8 | random 30 | total 38 |
|---|---|---|---|
| threshold disagreement (mild, visible finding called present, or borderline swelling) | 4 | 21 | 25 |
| risk-level judgment ("moderate" vs Low, "low" vs Elevated) | 3 | 4 | 7 |
| missed finding (stated absent, surgeon present) | 1 | 1 | 2 |
| checker error | 0 | 4 | 4 |
| **hallucination** | **0** | **0** | **0** |

The contradictions are lopsided: of 741 contradicted headline claims in condition A, 594 are erythema or edema called **present** where the surgeons graded it absent, and 25 the other way. The VLM is more sensitive, and the annotators' threshold is higher.

Published examples (each verified against the image):
- **274.jpg** (threshold): erythema present vs absent. "Present, localized. A pink-to-red halo surrounds the central purple lesion, extending a few millimeters to about 1 cm."
- **449.jpg** (threshold): erythema present vs absent. "Present, mild, and localized to the upper portion of the incision."
- **119.jpg** (missed finding): erythema absent vs present. "Assessment: No significant spreading redness is evident."
- **186.jpg** (threshold): edema present vs absent. "Present: Mild to moderate, likely."
- **984.jpg** (ID 900+, threshold): edema present vs absent. "Mild to moderate swelling appears present in the lower leg, ankle, and foot."
- **707.jpg** (risk judgment): elevated vs low. "Overall risk: moderate."
- **654.jpg** (risk judgment): elevated vs low. "Risk level: Moderate to high. This may be a superficial surgical site infection."
- **146.jpg** (risk judgment): low vs elevated. "Overall risk: LOW."

### All attributes (secondary; condition A exudate and healing are less reliably extracted)

| subset | report set | claims per report | correctness | claims contradicting surgeon labels |
|---|---|---|---|---|
| excl. 900+ | template | 3.6 | 0.82 [0.80, 0.85] | 0.16 [0.14, 0.19] |
| excl. 900+ | VLM B | 4.7 | 0.76 [0.73, 0.78] | 0.23 [0.21, 0.25] |
| excl. 900+ | VLM A | 5.9 | 0.62 [0.60, 0.64] | 0.36 [0.34, 0.38] |

Per attribute (excl. 900+, share of claims matching the label): template erythema 0.74, edema 0.86, exudate 0.92, infection 0.69; VLM B 0.62, 0.69, 0.82, 0.76; VLM A 0.44, 0.55, 0.51 (exudate, checker agreement 0.73), 0.85, and healing 0.52 (checker agreement 0.76).

## Perception is competitive: zero-shot VLM B vs our model

Stated plainly: **a zero-shot VLM, never trained on these labels, matches our supervised model's perception on infection risk and beats it on exudate.**

| head (excl. 900+) | n | macro F1 VLM B | macro F1 model A | difference | critical-class recall VLM B | model A |
|---|---|---|---|---|---|---|
| erythema | 591 | 0.61 [0.57, 0.64] | 0.61 [0.57, 0.66] | -0.01 [-0.06, +0.04] | 0.83 | 0.50 |
| edema | 497 | 0.59 [0.54, 0.64] | 0.65 [0.59, 0.71] | -0.06 [-0.12, -0.00] | 0.68 | 0.53 |
| exudate | 565 | 0.62 [0.55, 0.69] | 0.48 [0.41, 0.54] | **+0.15 [+0.05, +0.24]** | 0.69 (purulent) | 0.10 |
| infection | 613 | 0.64 [0.59, 0.68] | 0.62 [0.57, 0.66] | +0.02 [-0.03, +0.07] | 0.65 (elevated) | 0.64 |

| infection risk, excl. 900+ (prevalence 84 of 613) | Elevated recall | High-risk caught (n = 12) | false alarms per 100 | flagged per 100 |
|---|---|---|---|---|
| VLM B, native decision | 0.65 [0.54, 0.77] | **11 of 12** (0.92 [0.73, 1.00]) | 19.4 [16.1, 22.7] | 28.4 |
| model A, flag | 0.64 [0.54, 0.75] | **8 of 12** (0.67 [0.36, 0.92]) | 21.5 [17.9, 25.2] | 30.3 |
| model A, flag or refer | 0.86 [0.78, 0.93] | 10 of 12 (0.83 [0.58, 1.00]) | 43.1 [38.9, 47.0] | 54.8 |

At a similar alert rate the two tie on Elevated recall, and the VLM catches more High-risk wounds. **The VLM returns a single label with no score, so its decision cannot be threshold-tuned.** Possible contamination applies: the images were public and the dataset is public, so the VLM may have seen some of them.

**Conclusion.** Perception is competitive, not a differentiator. Our pipeline's value lies elsewhere:
- **grounding:** reports state only predicted attributes, with uncertainty made explicit (the A vs B gap shows this matters),
- **calibration:** confidence bands with observed rates (Phase 4),
- **a tunable operating point:** the flag-or-refer setting reaches 0.86 Elevated recall, which a fixed answer cannot,
- **referral:** low-confidence cases go to a clinician rather than to "on track",
- **on-device processing:** the model runs locally, so no patient photos are sent to a third party.

### Refusals

0 of 686 in condition A and 0 of 686 in condition B, at every infection-risk level (Low 573, Medium 90, High 23) and exudate class.

## Caveats

- **Effort `low`, one run.** Higher effort might strengthen the VLM baseline; run-to-run variation is unknown.
- **Possible contamination** of the VLM by the public images and dataset.
- **Labels are not independent of MLLM judgments:** SurgWound's annotation difficulty (one or two surgeons) was assigned from MLLM risk predictions.
- **The checker is rule-based and was redesigned after inspecting the VLM's outputs.** It is validated at 0.96 to 0.97 on the headline attributes for condition A, but not perfect, and it does not score location, closure or urgency.
- **Manual reviews are by a non-clinician**, from photos; "clearly absent" was applied conservatively.

## Notes for Phase 6 and next steps

- **Drainage comes from the patient's answer (unchanged).** The VLM's better purulent recall (0.69 vs 0.10) comes from a single zero-shot run with possible contamination, so it does not change the design.
- Patient-reported fever or worsening pain must be able to override a low-concern image band (2 of 12 High-risk images fall in that band).
- **Next step, not built: a hybrid.** Feed VLM-extracted exudate into the grounded template, keeping the template's structure and abstention. This would need the VLM call to run under the same data-handling terms, or a local VLM, to keep the on-device guarantee.
