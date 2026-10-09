# Phase 3: overlay mitigation, before vs after

Same folds, inner splits, seeds, candidate grid and decision rule. Only the input images differ.

## Classifier metrics (grouped 5-fold CV, fine-tuned, tuned decision rule)

| head | subset | macro F1 before | macro F1 after | critical AUROC before | critical AUROC after |
|---|---|---|---|---|---|
| erythema (present) | all | 0.62 [0.58, 0.66] | 0.63 [0.59, 0.67] | 0.71 [0.67, 0.75] | 0.70 [0.65, 0.74] |
| erythema (present) | excl_900plus | 0.61 [0.57, 0.65] | 0.61 [0.57, 0.66] | 0.69 [0.65, 0.74] | 0.68 [0.63, 0.73] |
| edema (present) | all | 0.63 [0.58, 0.68] | 0.63 [0.58, 0.68] | 0.76 [0.70, 0.81] | 0.74 [0.68, 0.79] |
| edema (present) | excl_900plus | 0.65 [0.59, 0.70] | 0.65 [0.59, 0.71] | 0.77 [0.70, 0.83] | 0.75 [0.68, 0.81] |
| exudate (purulent) | all | 0.43 [0.38, 0.48] | 0.47 [0.41, 0.52] | 0.76 [0.68, 0.83] | 0.74 [0.65, 0.83] |
| exudate (purulent) | excl_900plus | 0.43 [0.38, 0.48] | 0.48 [0.41, 0.54] | 0.77 [0.69, 0.84] | 0.76 [0.67, 0.84] |
| infection (elevated) | excl_900plus | 0.66 [0.61, 0.71] | 0.62 [0.57, 0.66] | 0.77 [0.71, 0.82] | 0.77 [0.71, 0.82] |
| infection (elevated) | all | 0.69 [0.64, 0.73] | 0.64 [0.59, 0.68] | 0.80 [0.75, 0.84] | 0.79 [0.74, 0.84] |

High-risk recall (excl_900plus, n High = 12): before 0.42 [0.13, 0.70], after 0.67 [0.36, 0.92]

High-risk recall (all, n High = 23): before 0.70 [0.48, 0.88], after 0.83 [0.67, 0.96]

Frozen-feature baseline, infection critical AUROC (all / excl. 900+): before (original images): 0.77 [0.72, 0.82] / 0.74 [0.67, 0.80]; after (overlays inpainted): 0.76 [0.71, 0.81] / 0.73 [0.67, 0.79]

### Paired test, mitigated minus original (same group resamples, `scripts/phase3_paired_test.py`)

| head | subset | n | macro F1 diff | critical AUROC diff | critical recall diff |
|---|---|---|---|---|---|
| erythema | all | 660 | +0.008 [-0.020, +0.033] | -0.012 [-0.030, +0.006] | +0.016 [-0.032, +0.062] |
| erythema | excl_900plus | 591 | +0.007 [-0.022, +0.039] | -0.016 [-0.037, +0.005] | +0.025 [-0.030, +0.083] |
| edema | all | 554 | -0.002 [-0.035, +0.027] | -0.018 [-0.040, +0.001] | -0.012 [-0.093, +0.060] |
| edema | excl_900plus | 497 | +0.002 [-0.033, +0.035] | -0.016 [-0.038, +0.003] | +0.000 [-0.078, +0.074] |
| exudate | all | 626 | +0.037 [-0.007, +0.088] | -0.013 [-0.056, +0.034] | +0.067 [+0.000, +0.174] |
| exudate | excl_900plus | 565 | +0.046 [-0.000, +0.099] | -0.010 [-0.057, +0.036] | +0.069 [+0.000, +0.179] |
| infection | excl_900plus | 613 | -0.046 [-0.083, -0.010] | -0.004 [-0.029, +0.021] | +0.071 [-0.011, +0.152] |
| infection | all | 686 | -0.048 [-0.077, -0.019] | -0.007 [-0.025, +0.014] | +0.062 [+0.000, +0.122] |

High-risk recall diff (excl_900plus, n High = 12): +0.250 [+0.000, +0.545]

High-risk recall diff (all, n High = 23): +0.130 [+0.000, +0.286]

**Reading:** the infection macro F1 drop is significant, but ranking is unchanged (AUROC diff near 0). The tuned decision rule of the mitigated model calls more images elevated (excl. 900+: 141 vs 88; false alarms 99 vs 52), mostly because one fold's inner-val chose a stronger prior correction. This is a threshold shift, not a change in what the model ranks; the High-risk recall change has the same cause and is not attributed to the mitigation. Phase 4 sets the infection operating point by a recall target instead.

## Source probe: AUROC for predicting ID 900+ from image features

| features | before | after |
|---|---|---|
| frozen pretrained ConvNeXt-Tiny | 0.93 [0.88, 0.97] | 0.93 [0.88, 0.96] |
| fine-tuned (CV fold models) | 0.92 [0.88, 0.95] | 0.89 [0.83, 0.94] |

## Grad-CAM mass on overlay regions (overlay images only)

Excess = CAM mass share on overlay boxes minus their area share (0 means no preference). After mitigation the boxes mark where overlays used to be.

| head | subset | n | area share | CAM mass before | excess before | CAM mass after | excess after |
|---|---|---|---|---|---|---|---|
| erythema | all_overlay_images | 74 | 0.053 | 0.08 [0.05, 0.10] | +0.023 [+0.006, +0.044] | 0.04 [0.03, 0.05] | -0.017 [-0.026, -0.009] |
| erythema | id_900plus | 28 | 0.081 | 0.13 [0.10, 0.16] | +0.045 [+0.017, +0.077] | 0.05 [0.03, 0.08] | -0.028 [-0.045, -0.011] |
| erythema | other_sources | 46 | 0.035 | 0.05 [0.02, 0.08] | +0.010 [-0.009, +0.037] | 0.03 [0.02, 0.04] | -0.010 [-0.019, -0.003] |
| edema | all_overlay_images | 74 | 0.053 | 0.08 [0.05, 0.10] | +0.023 [+0.001, +0.046] | 0.03 [0.02, 0.05] | -0.018 [-0.031, -0.008] |
| edema | id_900plus | 28 | 0.081 | 0.11 [0.07, 0.16] | +0.028 [-0.013, +0.075] | 0.04 [0.03, 0.06] | -0.037 [-0.063, -0.014] |
| edema | other_sources | 46 | 0.035 | 0.05 [0.03, 0.09] | +0.019 [-0.002, +0.047] | 0.03 [0.02, 0.04] | -0.007 [-0.016, +0.002] |
| exudate | all_overlay_images | 74 | 0.053 | 0.06 [0.05, 0.08] | +0.010 [-0.006, +0.024] | 0.03 [0.02, 0.04] | -0.024 [-0.035, -0.013] |
| exudate | id_900plus | 28 | 0.081 | 0.11 [0.08, 0.14] | +0.030 [+0.000, +0.058] | 0.04 [0.02, 0.05] | -0.045 [-0.064, -0.027] |
| exudate | other_sources | 46 | 0.035 | 0.03 [0.02, 0.05] | -0.002 [-0.017, +0.013] | 0.02 [0.02, 0.03] | -0.011 [-0.023, +0.001] |
| infection | all_overlay_images | 74 | 0.053 | 0.09 [0.06, 0.11] | +0.033 [+0.014, +0.052] | 0.02 [0.01, 0.03] | -0.031 [-0.044, -0.019] |
| infection | id_900plus | 28 | 0.081 | 0.14 [0.10, 0.17] | +0.055 [+0.016, +0.094] | 0.03 [0.01, 0.04] | -0.056 [-0.076, -0.037] |
| infection | other_sources | 46 | 0.035 | 0.05 [0.03, 0.08] | +0.019 [+0.004, +0.039] | 0.02 [0.01, 0.03] | -0.016 [-0.030, -0.002] |

## Causal check: change in P(critical class) when overlays are inpainted at test time

Before: the original model, original vs inpainted input. After: the mitigated model on the same pair. Negative = overlays push toward the critical class.

| head | subset | n | mean dP before | flips before | mean dP after | flips after |
|---|---|---|---|---|---|---|
| erythema | all_overlay_images | 74 | -0.016 [-0.030, -0.002] | 7 | +0.016 [+0.003, +0.029] | 2 |
| erythema | id_900plus | 28 | -0.024 [-0.042, -0.002] | 0 | +0.022 [+0.003, +0.043] | 0 |
| erythema | other_sources | 46 | -0.011 [-0.030, +0.006] | 7 | +0.013 [-0.005, +0.030] | 2 |
| edema | all_overlay_images | 74 | -0.014 [-0.025, -0.005] | 4 | -0.001 [-0.011, +0.010] | 4 |
| edema | id_900plus | 28 | -0.025 [-0.046, -0.007] | 3 | +0.003 [-0.019, +0.025] | 3 |
| edema | other_sources | 46 | -0.008 [-0.019, +0.002] | 1 | -0.003 [-0.014, +0.007] | 1 |
| exudate | all_overlay_images | 74 | -0.006 [-0.011, -0.002] | 3 | -0.003 [-0.007, +0.000] | 1 |
| exudate | id_900plus | 28 | -0.013 [-0.022, -0.005] | 2 | -0.009 [-0.017, -0.002] | 0 |
| exudate | other_sources | 46 | -0.002 [-0.006, +0.001] | 1 | +0.000 [-0.003, +0.004] | 1 |
| infection | all_overlay_images | 74 | -0.043 [-0.061, -0.028] | 4 | -0.006 [-0.014, +0.002] | 0 |
| infection | id_900plus | 28 | -0.079 [-0.119, -0.046] | 3 | -0.005 [-0.020, +0.009] | 0 |
| infection | other_sources | 46 | -0.022 [-0.036, -0.011] | 1 | -0.006 [-0.016, +0.003] | 0 |
