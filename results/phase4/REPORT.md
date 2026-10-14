# Phase 4: Calibration, operating points and abstention

Model: A (mitigated, inpainted inputs). Protocol: grouped 5-fold CV, pooled out-of-fold predictions. Every quantity that is fit (temperatures, thresholds, abstention cut-offs) is fit per outer fold on that fold's inner-val split only.

Reproduce: `python scripts/phase4_calibrate.py` (CPU, about 5 min). Full tables: `tables.md`; numbers: `metrics.json`; per-fold temperatures: `temperatures.json`. Figures: `reliability_{all,excl_900plus}.png`, `operating_points.png`, `abstention_infection.png`, `abstention_other_heads.png`.

## Headline

1. **Temperature scaling does not help.** The model is already close to calibrated on top-label confidence (ECE 0.03 to 0.05). Scaling fit on about 88 inner-val images changes no head's ECE significantly, and NLL gets slightly worse. The remaining miscalibration is in the *shape*: P(critical) above about 0.6 over-predicts (for infection, predicted 0.75 to 0.85 corresponds to an observed rate of about 0.3). A single temperature cannot fix that.
2. **Recall targets set on inner-val are not met out-of-fold.** Aiming for 0.8 recall on Elevated delivers **0.64 [0.54, 0.75]** excluding ID 900+. Inner-val holds only 8 to 18 Elevated images per fold, and it was already used for model selection, so it is optimistic. To actually reach about 0.85 recall, the "0.9" setting is needed: **0.87 [0.79, 0.94] recall at 44 [39, 48] false alarms per 100 images**, 3.7 false alarms per Elevated case caught.
3. **Abstention on a binary head is a second threshold.** Referring uncertain "Low" calls for review cuts missed Elevated cases from 4.9 to 2.0 per 100 images, but it raises clinician workload from 30 to 55 per 100. That is almost the same trade-off as lowering the flag threshold. Its value is in the product, not the statistics: a three-level output (flag / review / routine) that maps directly onto the Phase 6 verdicts.

## 1. Calibration

| head | subset | n | ECE before | ECE after | paired diff | class ECE (critical) before | after |
|---|---|---|---|---|---|---|---|
| erythema | excl. 900+ | 591 | 0.049 [0.026, 0.087] | 0.050 [0.027, 0.090] | +0.001 [-0.025, +0.030] | 0.087 | 0.100 |
| edema | excl. 900+ | 497 | 0.028 [0.018, 0.062] | 0.027 [0.017, 0.064] | -0.001 [-0.023, +0.027] | 0.108 | 0.097 |
| exudate | excl. 900+ | 565 | 0.044 [0.033, 0.076] | 0.028 [0.019, 0.061] | -0.016 [-0.040, +0.014] | 0.025 | 0.024 |
| infection | excl. 900+ | 613 | 0.028 [0.018, 0.064] | 0.034 [0.019, 0.067] | +0.007 [-0.012, +0.021] | 0.075 | 0.079 |
| infection | all | 686 | 0.040 [0.025, 0.074] | 0.045 [0.028, 0.078] | +0.005 [-0.012, +0.019] | 0.085 | 0.090 |

NLL and Brier score (in `tables.md`) are unchanged or slightly worse after scaling for every head.
Fitted temperatures vary widely across folds (infection 0.87 to 1.49, edema 0.59 to 1.01), so with about 88 inner-val images the temperature mostly fits noise.
The top-label ECE looks good partly because most images are confidently "none / low"; the class-level reliability of P(critical) (`reliability_*.png`) is the more useful view and shows over-prediction at high probabilities.

**Consequence for the product:** probabilities should be treated as rank scores with calibrated *cut-offs*, not shown to users as percentages. The app should show bands (for example "low / uncertain / high concern"), not "73%".

## 2. Infection operating point by recall target

Threshold per fold chosen on inner-val so that inner-val recall on Elevated reaches the target; applied to that fold's held-out images.

| target (set on inner-val) | subset | recall on Elevated | High-risk recall | specificity | PPV | flagged per 100 | false alarms per 100 | false alarms per Elevated caught |
|---|---|---|---|---|---|---|---|---|
| 0.7 | excl. 900+ (n=613) | 0.51 [0.41, 0.61] | 0.50 [0.20, 0.80] (n=12) | 0.80 [0.77, 0.84] | 0.29 [0.22, 0.36] | 24.3 | 17.3 [14.0, 20.3] | 2.5 [1.8, 3.6] |
| 0.8 | excl. 900+ (n=613) | 0.64 [0.54, 0.75] | 0.67 [0.36, 0.92] (n=12) | 0.75 [0.71, 0.79] | 0.29 [0.22, 0.36] | 30.3 | 21.5 [17.9, 25.2] | 2.4 [1.8, 3.5] |
| 0.9 | excl. 900+ (n=613) | **0.87 [0.79, 0.94]** | 0.83 [0.58, 1.00] (n=12) | 0.49 [0.44, 0.54] | 0.21 [0.17, 0.26] | 55.8 | **43.9 [39.4, 48.2]** | 3.7 [2.9, 4.8] |
| 0.7 | all (n=686) | 0.62 [0.52, 0.71] | 0.74 [0.54, 0.92] (n=23) | 0.77 [0.74, 0.81] | 0.35 [0.28, 0.41] | 29.3 | 19.1 [16.2, 22.1] | 1.9 [1.4, 2.6] |
| 0.8 | all (n=686) | 0.72 [0.63, 0.80] | 0.83 [0.67, 0.96] (n=23) | 0.72 [0.68, 0.76] | 0.33 [0.27, 0.40] | 35.3 | 23.5 [20.1, 26.8] | 2.0 [1.5, 2.7] |
| 0.9 | all (n=686) | 0.90 [0.84, 0.95] | 0.91 [0.77, 1.00] (n=23) | 0.47 [0.43, 0.52] | 0.25 [0.21, 0.30] | 58.9 | 44.0 [40.1, 48.0] | 3.0 [2.3, 3.8] |

Prevalence of Elevated is 14% excluding 900+ (84/613), so even a perfect-recall system would flag at least 14 per 100. Each Elevated case found costs 2.4 to 3.7 false alarms.
Per-fold thresholds vary several-fold (target 0.8: 0.12 to 0.48 on calibrated P(elevated)); see `tables.md`.
`operating_points.png` shows the full pooled out-of-fold curve (descriptive only, not used to pick anything) with the three achieved points and their CIs.

## 3. Abstention ("send for review")

### Infection, decision at the "0.8" operating point

Only Low calls can be referred (a flag already goes to a clinician). Cut-off tau per fold = inner-val confidence quantile for the target coverage.

| target coverage | subset | achieved coverage | missed Elevated per 100 | Elevated flagged or referred | High-risk flagged or referred | workload (flagged + referred) per 100 |
|---|---|---|---|---|---|---|
| 1.0 (no abstention) | excl. 900+ | 1.00 | 4.9 [3.2, 6.7] | 0.64 [0.54, 0.75] | 0.67 [0.36, 0.92] (n=12) | 30.3 [26.1, 34.4] |
| 0.9 | excl. 900+ | 0.86 [0.83, 0.89] | 3.3 [1.9, 4.8] | 0.76 [0.66, 0.85] | 0.75 [0.46, 1.00] (n=12) | 44.0 [39.4, 48.5] |
| 0.8 | excl. 900+ | 0.76 [0.72, 0.79] | 2.0 [0.9, 3.1] | 0.86 [0.78, 0.93] | 0.83 [0.58, 1.00] (n=12) | 54.8 [50.3, 58.9] |
| 0.7 | excl. 900+ | 0.66 [0.62, 0.70] | 1.3 [0.5, 2.3] | 0.90 [0.84, 0.96] | 0.83 [0.58, 1.00] (n=12) | 64.3 [60.2, 68.1] |
| 0.8 | all | 0.77 [0.74, 0.80] | 1.7 [0.9, 2.7] | 0.89 [0.83, 0.95] | 0.91 [0.77, 1.00] (n=23) | 58.3 [54.5, 62.3] |

Compare the 0.8-coverage row (0.86 caught, 55 per 100 workload) with the "0.9" operating point without abstention (0.87 recall, 56 flagged per 100): for a binary head they are nearly the same system. `abstention_infection.png` shows the full coverage curves (missed Elevated, caught, workload).

### Other heads (calibrated argmax), all images

| head | target coverage | achieved | accuracy on answered | critical recall on answered | critical cases referred |
|---|---|---|---|---|---|
| erythema | 1.0 | 1.00 | 0.70 [0.66, 0.73] | 0.45 [0.38, 0.52] | 0.00 |
| erythema | 0.8 | 0.77 | 0.75 [0.71, 0.79] | 0.43 [0.35, 0.52] | 0.32 [0.25, 0.40] |
| edema | 1.0 | 1.00 | 0.77 [0.74, 0.81] | 0.43 [0.32, 0.55] | 0.00 |
| edema | 0.8 | 0.82 | 0.84 [0.80, 0.87] | 0.41 [0.26, 0.56] | 0.28 [0.18, 0.39] |
| exudate | 1.0 | 1.00 | 0.82 [0.79, 0.85] | 0.07 [0.00, 0.16] | 0.00 |
| exudate | 0.8 | 0.78 | 0.92 [0.90, 0.95] | 0.00 [0.00, 0.00] | 0.70 [0.53, 0.86] |

Abstention raises accuracy on answered cases but does not improve recall of the critical class among answered cases. For exudate it routes 70% of purulent wounds to review, yet the model never correctly names purulent on the cases it answers. That supports the Phase 2 decision: drainage in the verdict comes from the patient.

## Caveats

- **Inner-val is reused** for checkpoint selection, the decision rule, temperatures, recall thresholds and abstention cut-offs. The under-delivered recall targets are the visible cost. A product needs a separate calibration set; here none exists without shrinking training further.
- **Small positive counts:** 84 Elevated and 12 High-risk images excluding 900+. High-risk intervals span 0.3 to 0.4.
- **Deployment uses a 5-model ensemble**, which these per-fold numbers do not evaluate directly. Phase 6 will use per-fold thresholds averaged across folds and must state that this setting is unvalidated. (Superseded in Phase 7: the demo uses the fold 0 model alone, with the thresholds evaluated for fold 0.)

## Decisions recorded

1. **No temperature scaling.** Decisions, thresholds and bands use the unscaled probabilities. For a binary head per-fold scaling is monotone, so the operating-point and abstention results are unchanged (one workload figure moves from 58.3 to 58.2 per 100 through quantile interpolation). The calibration table above stays as the evidence for this decision.
2. **Operating point: the "0.8" setting plus referral at 80% coverage**, giving three levels for Phase 6. Achieved out-of-fold, excluding ID 900+: **0.86 [0.78, 0.93] of Elevated images flagged or referred**, missed 2.0 [0.9, 3.1] per 100, **clinician workload 54.8 [50.3, 58.9] per 100**, against an Elevated prevalence of 84 of 613 (14%). The inner-val recall target was not met out-of-fold: inner-val slices hold only 8 to 18 Elevated images, and the same slice was already used for model selection, which makes it optimistic.
3. **Displayed output is a band with its observed rate, not a probability:**

| band (infection risk) | rule on P(elevated) | excl. 900+: n (share) | observed Elevated rate, excl. 900+ | High-risk in band | all images: n | observed rate, all |
|---|---|---|---|---|---|---|
| low concern | below t_review | 277 (45%) | **4% [2, 7]** (12 of 277) | 2 | 287 | 4% [2, 6] |
| uncertain (refer for review) | t_review to t_flag | 150 (24%) | **12% [7, 17]** (18 of 150) | 2 | 157 | 13% [8, 18] |
| high concern (flag) | t_flag and above | 186 (30%) | **29% [22, 36]** (54 of 186) | 8 | 242 | 33% [27, 40] |

Cut-offs are per fold from inner-val (t_review 0.03 to 0.18, t_flag 0.08 to 0.48). For the deployed 5-model ensemble, `operating_point.json` stores the fold means (t_review 0.103, t_flag 0.252). That ensemble setting is **not evaluated** by this cross-validation, and the wide spread of per-fold cut-offs means it should be treated as provisional. Two High-risk images (both excluding 900+) fall in the low-concern band; these are the system's misses.
