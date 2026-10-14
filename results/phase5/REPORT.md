# Phase 5: Grounded report generation and faithfulness check

Reproduce (all paths relative to the repo root):
```
python scripts/phase5_reports.py              # template reports, checker validation on expert reports
python scripts/phase5_vlm.py prepare          # VLM inputs (no API calls)
python scripts/phase5_vlm.py pilot            # 4 requests, cost projection (API, about $0.10)
python scripts/phase5_vlm.py submit --runs run1
python scripts/phase5_vlm.py collect          # download, map back locally, delete the batch
python scripts/phase5_markdown_validation.py  # checker vs hand labels on 30 condition A reports
python scripts/phase5_compare.py              # all comparisons below
```
Tables: `tables.md` (template, checker validation on expert reports), `vlm/comparison.md` (VLM comparison), `markdown_validation.json` and `markdown_validation_labels.csv` (hand-label validation). Raw VLM outputs keyed by image name: `vlm/vlm_outputs.parquet`.

## Headline

- **Grounded template reports make fewer wrong claims than the zero-shot VLM.** On erythema, edema and infection risk (the attributes where the claim checker is validated for all three report sets), excluding ID 900+ (n = 613):
  - template claims agree with the surgeon labels **0.76 [0.73, 0.79]** of the time,
  - VLM condition B (structured answer, rendered by our template) **0.69 [0.66, 0.72]**, paired difference -0.07 [-0.10, -0.04],
  - VLM condition A (free-text report) **0.62 [0.60, 0.64]**, paired difference -0.14 [-0.18, -0.11].
- **Hallucination rate** (claims that contradict the expert label, share of all claims), same attributes: template 0.22 [0.19, 0.25], condition B 0.29 [0.26, 0.31], condition A 0.35 [0.33, 0.37]. 73% of condition A reports contain at least one contradiction on these three attributes, against 40% of template reports.
- **As a zero-shot classifier, the VLM ties our model on infection risk and beats it on exudate.** Condition B infection: Elevated recall 0.65 [0.54, 0.77] at 19.4 false alarms per 100, versus model A's flag 0.64 [0.54, 0.75] at 21.5. Exudate macro F1 0.62 vs 0.48 (difference +0.15 [+0.05, +0.24]); purulent recall 0.69 vs 0.10.
- **No refusals** in either condition (0 of 1,372 requests). The primary scoring mode (refusals counted as incorrect) and the secondary mode (refusals excluded) are therefore identical in this run.

## Setup

**Template reports (ours).** Rendered only from model A's out-of-fold attribute JSON (`src/report/template.py`): erythema, edema, exudate (stated as unreliable, drainage comes from the patient), and infection risk as its Phase 4 band with the band's observed rate. Attributes in the "uncertain" abstention zone are stated as uncertain and make no claim. No location, closure or healing status is stated, since the model does not predict them.

**VLM baseline.** Claude Opus 5.5 (`claude-opus-5-5`) via the Message Batches API, zero-shot, one run per image (686 images x 2 conditions = 1,372 requests).
- **Condition A, free text:** the SurgWound report-task instruction, verbatim.
- **Condition B, structured:** a JSON schema restricted to exactly our label options (erythema none/present, edema none/present, exudate none/non_purulent/purulent, infection risk low/elevated). The JSON is rendered by our template generator, so B differs from the template only in where the attributes come from.
- **Both conditions ran at effort `low`, with identical settings, because of budget.** The full plan at the default effort projected $28.74 and at `low` $20.64; the two repeat runs on the official test split were then dropped to stay under the $15 cap (projection $14.75). Higher effort might strengthen the VLM baseline, and run-to-run variation was not measured.
- Actual cost: **$15.58** for the batch (1,375,196 input and 1,282,962 output tokens at batch prices), plus about $0.22 for two 4-request pilots. The projection from 2 samples per condition underestimated slightly.
- **Data handling:** only inpainted images were sent (text, account numbers and redaction boxes removed), re-encoded from raw pixels (no EXIF or other metadata), long side at most 1024 px, inline base64, with random opaque request IDs. No file names, labels or IDs were sent. The batch was deleted after download. Anthropic terms and links: README.

**Scoring.** Every report is reduced to claims (attribute, value) and each claim is compared with the SurgWound expert label: supported, contradicted, or unverifiable (label Uncertain). Correctness = supported / (supported + contradicted). Primary: refusals and failed requests count as incorrect for every labeled attribute of that image (none occurred). Group-bootstrap 95% CIs (patient groups), paired differences on the same resamples. Primary subset excludes ID 900+.

## The claim checker, and why condition A needed its own

The prose extractor (`src/report/claims.py`) agrees with the expert labels on 87 to 98% of attributes when run on the expert reports themselves (`tables.md`), and the template's faithfulness to its own JSON is 1.000.

Condition A's reports are different: about 4,500 characters of markdown with one section per requested aspect, tables, and lists of warning signs ("seek care if: purulent discharge, spreading redness"). Run over whole reports, the prose extractor read headings ("### Erythema") and warning-sign lists as findings. In a hand review of 15 of its contradictions, 8 were checker errors.

A section-aware extractor (`src/report/markdown_claims.py`) reads each attribute only from its own section, up to the first escalation or advice list, and ignores headings, tables and recommendation sections. It was developed on separate reports, frozen, and then validated once against hand labels on 30 random condition A reports (labels written from the report text before seeing the extractor's output; 10 of 150 judgments were genuinely ambiguous and excluded):

| attribute | n | agreement, section-aware | agreement, prose extractor |
|---|---|---|---|
| erythema | 29 | 0.97 | 0.21 |
| edema | 26 | 0.96 | 0.08 |
| infection risk | 30 | 0.97 | 0.43 |
| exudate | 30 | 0.73 | 0.17 |
| healing status | 25 | 0.76 | 0.48 |
| all | 140 | 0.88 | 0.27 |

Headline comparisons therefore use erythema, edema and infection only. Exudate and healing results for condition A are reported but carry the lower agreement. A known gap: about 1% of condition A reports use bold-text headings instead of markdown headings and yield no claims; the extractor was not changed after validation.

## Results

### Headline: erythema, edema, infection risk

| subset | report set | n | claims per report | correctness | hallucination rate | reports with a contradiction |
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

Paired differences against the template (excl. 900+): VLM A correctness -0.14 [-0.18, -0.11], hallucination +0.13 [+0.10, +0.17]; VLM B correctness -0.07 [-0.10, -0.04], hallucination +0.07 [+0.04, +0.10]. The template makes fewer claims because uncertain predictions are stated as uncertain; that abstention is part of why its claims are more often right.

### All attributes (secondary; condition A exudate and healing are less reliably extracted)

| subset | report set | claims per report | correctness | hallucination rate |
|---|---|---|---|---|
| excl. 900+ | template | 3.6 | 0.82 [0.80, 0.85] | 0.16 [0.14, 0.19] |
| excl. 900+ | VLM B | 4.7 | 0.76 [0.73, 0.78] | 0.23 [0.21, 0.25] |
| excl. 900+ | VLM A | 5.9 | 0.62 [0.60, 0.64] | 0.36 [0.34, 0.38] |

Per attribute (excl. 900+, share of claims that match the label): template erythema 0.74, edema 0.86, exudate 0.92, infection 0.69; VLM B 0.62, 0.69, 0.82, 0.76; VLM A 0.44, 0.55, 0.51 (exudate, checker agreement 0.73), 0.85, and healing 0.52 (checker agreement 0.76). Condition A also states wound location, closure method and urgency, which the checker does not score.

### Condition B as a zero-shot classifier (excl. 900+)

| head | n | macro F1 VLM B | macro F1 model A | difference | critical-class recall VLM B | model A |
|---|---|---|---|---|---|---|
| erythema | 591 | 0.61 [0.57, 0.64] | 0.61 [0.57, 0.66] | -0.01 [-0.06, +0.04] | 0.83 | 0.50 |
| edema | 497 | 0.59 [0.54, 0.64] | 0.65 [0.59, 0.71] | -0.06 [-0.12, -0.00] | 0.68 | 0.53 |
| exudate | 565 | 0.62 [0.55, 0.69] | 0.48 [0.41, 0.54] | **+0.15 [+0.05, +0.24]** | 0.69 (purulent) | 0.10 |
| infection | 613 | 0.64 [0.59, 0.68] | 0.62 [0.57, 0.66] | +0.02 [-0.03, +0.07] | 0.65 (elevated) | 0.64 |

Infection risk at each system's decision (excl. 900+; prevalence 84 of 613). **The VLM returns a single label with no score, so its decision cannot be threshold-tuned**; it is compared at its native decision:

| system | Elevated recall | High-risk caught (n = 12) | false alarms per 100 | flagged per 100 |
|---|---|---|---|---|
| VLM B, native decision | 0.65 [0.54, 0.77] | 0.92 [0.73, 1.00] | 19.4 [16.1, 22.7] | 28.4 |
| model A, flag | 0.64 [0.54, 0.75] | 0.67 [0.36, 0.92] | 21.5 [17.9, 25.2] | 30.3 |
| model A, flag or refer | 0.86 [0.78, 0.93] | 0.83 [0.58, 1.00] | 43.1 [38.9, 47.0] | 54.8 |

At a matched alert rate the VLM and model A perform about the same on Elevated risk, and the VLM catches more High-risk wounds (11 vs 8 of 12). Model A's advantage is that it can be moved along its curve: the flag-or-refer setting reaches 0.86 recall, which the VLM's fixed answer cannot.

### Refusals

0 of 686 in condition A and 0 of 686 in condition B, at every infection-risk level (Low 573, Medium 90, High 23) and exudate class. The refusal tables in `vlm/comparison.md` are therefore all zero.

### Examples: condition A contradicting the expert labels

Drawn at random from contradicted claims on the validated attributes; each reflects the report text, not a checker error.

- **274.jpg**: erythema claimed present, label absent. "Present, localized. A pink-to-red halo surrounds the central purple lesion, extending a few millimeters to about 1 cm."
- **449.jpg**: erythema claimed present, label absent. "Present, mild, and localized to the upper portion of the incision."
- **119.jpg**: erythema claimed absent, label present. "Assessment: No significant spreading redness is evident."
- **186.jpg**: edema claimed present, label absent. "Present: Mild to moderate, likely."
- **984.jpg** (ID 900+): edema claimed present, label absent. "Mild to moderate swelling appears present in the lower leg, ankle, and foot."
- **707.jpg**: infection risk claimed elevated, label low. "Overall risk: moderate."
- **654.jpg**: infection risk claimed elevated, label low. "Risk level: Moderate to high. This may be a superficial surgical site infection."
- **146.jpg**: infection risk claimed low, label elevated. "Overall risk: LOW."

Many disagreements are about a threshold rather than an invented finding: the VLM calls mild, localized pinkness "erythema present" where the surgeons graded it absent. The checker cannot tell a threshold disagreement from a fabricated finding, so "hallucination rate" here means "contradicts the expert label".

## Caveats

- **Effort `low`, one run.** Higher effort might strengthen the VLM baseline, and run-to-run variation is unknown.
- **Possible contamination:** the images were public and the dataset is public, so the VLM may have seen some of them.
- **Labels are not independent of MLLM judgments:** SurgWound's annotation difficulty (one or two surgeons) was assigned from MLLM risk predictions.
- **The checker is rule-based.** It is validated at 0.96 to 0.97 on the headline attributes for condition A, but not perfect, and it does not score location, closure or urgency.
- **The template's infection claims use model A's band**, which was tuned on inner-val; condition B's come from a single zero-shot call. Both are evaluated on the same out-of-fold images.

## Notes for Phase 6

- Patient-reported fever or worsening pain must be able to override a low-concern image band (2 of 12 High-risk images fall in that band).
- Drainage comes from the patient's answer. The VLM's much better purulent recall (0.69 vs 0.10) is worth noting, but it is a single zero-shot run with possible contamination, so it does not change that design choice.
