# Phase 2: Multi-task classifier

Reproduce (all paths are relative to the repo root):
```
python scripts/phase2_train.py   # about 50 min on an RTX 4060 laptop GPU
python scripts/phase2_eval.py    # about 15 min, mostly bootstrap
```
Config: `configs/phase2_convnext_tiny.yaml`. Full tables: `convnext_tiny_384/metrics.md`, raw numbers: `convnext_tiny_384/metrics.json`, per-image logits: `convnext_tiny_384/logits.parquet`, fold assignment: `splits.csv`, inner splits: `inner_splits.json`.
Training is bit-for-bit deterministic (a rerun of the same fold gives identical logits).

## Headline

**Fine-tuning ConvNeXt-Tiny clearly helps only erythema, and only in ranking (critical-class AUROC +0.07 [+0.03, +0.12]). It ties the frozen-feature baseline on every other head and on macro F1 for all heads.** Infection performance is partly carried by one image source (IDs 900+), and both models encode that source almost perfectly (probe AUROC 0.92 to 0.93).

## Setup

- **Heads:** erythema (none / present), edema (none / present), exudate (none / non-purulent / purulent), infection (low / elevated = Medium + High). Missing ("Uncertain") labels are masked from loss and metrics.
- **Model:** ConvNeXt-Tiny (`convnext_tiny.fb_in22k_ft_in1k`), 384 px letterboxed input (padded, never cropped), one linear head per attribute, fp16 mixed precision, AdamW, cosine schedule, drop path 0.1, loss = sum of per-head cross-entropy with sqrt inverse class-frequency weights.
- **Augmentation:** random resized crop (scale 0.6 to 1), flips, rotation 15 degrees, brightness/contrast 0.1, saturation 0.05, no hue shift (redness is a signal).
- **Baseline:** logistic regression (balanced class weights, C by grouped inner CV) on frozen ConvNeXt-Tiny features.
- **Primary protocol:** grouped 5-fold CV over all 686 images, groups from the broad automatic same-patient rule (no group spans two folds). Metrics are pooled over out-of-fold predictions.
- **Secondary protocol:** official test minus the 12 test images with a verified same-patient partner in train/val and the in-test duplicate 124.jpg (124 images). Training uses official train+val minus all 78 images sharing a broad-rule group with any remaining test image (471 images).
- **What touches what.** Each outer fold splits its training part (grouped) into inner-train and inner-val (1/6, about 88 images). Both models are fit on inner-train only. Inner-val is used for (1) the fine-tuned model's learning-rate candidate and epoch (nested, 3 candidates, lowest inner-val loss) and (2) both models' decision rule. Evaluation-fold images never influence training, selection or thresholds. The learning-rate grid was set after one look at fold-0 inner-val curves.
- **Decision rule** (`src/eval/thresholds.py`): predict argmax of log p(c) minus alpha times log prior(c), where prior is the inner-train class frequency. One alpha per head per fold, chosen to maximize inner-val macro F1 (alpha 0 = argmax, 1 = full prior correction; for binary heads this is a probability threshold). One parameter was used instead of free per-class thresholds because inner-val holds only 1 to 7 purulent and 5 to 14 edema-present images per fold.
- **CIs:** 95% percentile intervals from 2,000 bootstrap resamples of same-patient groups. Fine-tuned minus baseline uses a paired bootstrap (same resamples).

## Main results: grouped 5-fold CV (tuned decision rule)

For infection, the ID 900+ excluded estimate is listed first and is the primary honest estimate.

| head (critical class) | subset | n | macro F1 FT | macro F1 baseline | diff | critical AUROC FT | critical AUROC baseline | diff |
|---|---|---|---|---|---|---|---|---|
| erythema (present) | all | 660 | 0.62 [0.58, 0.66] | 0.59 [0.56, 0.63] | +0.03 [-0.01, +0.07] | 0.71 [0.67, 0.75] | 0.64 [0.59, 0.69] | **+0.07 [+0.03, +0.12]** |
| erythema (present) | excl. 900+ | 591 | 0.61 [0.57, 0.65] | 0.58 [0.54, 0.63] | +0.02 [-0.02, +0.07] | 0.69 [0.65, 0.74] | 0.63 [0.57, 0.69] | **+0.06 [+0.01, +0.11]** |
| edema (present) | all | 554 | 0.63 [0.58, 0.68] | 0.63 [0.58, 0.67] | +0.01 [-0.03, +0.05] | 0.76 [0.70, 0.81] | 0.74 [0.68, 0.80] | +0.02 [-0.03, +0.07] |
| edema (present) | excl. 900+ | 497 | 0.65 [0.59, 0.70] | 0.63 [0.58, 0.68] | +0.02 [-0.03, +0.06] | 0.77 [0.70, 0.83] | 0.74 [0.67, 0.80] | +0.03 [-0.02, +0.08] |
| exudate (purulent) | all | 626 | 0.43 [0.38, 0.48] | 0.44 [0.39, 0.49] | -0.01 [-0.07, +0.05] | 0.76 [0.68, 0.83] | 0.72 [0.61, 0.82] | +0.04 [-0.10, +0.17] |
| exudate (purulent) | excl. 900+ | 565 | 0.43 [0.38, 0.48] | 0.45 [0.40, 0.50] | -0.02 [-0.08, +0.05] | 0.77 [0.69, 0.84] | 0.74 [0.64, 0.84] | +0.02 [-0.10, +0.16] |
| **infection (elevated)** | **excl. 900+** | **613** | **0.66 [0.61, 0.71]** | **0.63 [0.58, 0.68]** | +0.03 [-0.02, +0.08] | **0.77 [0.71, 0.82]** | **0.74 [0.67, 0.80]** | +0.03 [-0.03, +0.10] |
| infection (elevated) | all | 686 | 0.69 [0.64, 0.73] | 0.66 [0.62, 0.71] | +0.02 [-0.02, +0.07] | 0.80 [0.75, 0.84] | 0.77 [0.72, 0.82] | +0.03 [-0.02, +0.08] |

**High-risk images predicted elevated:**
- excluding 900+, **n High = 12**: fine-tuned 0.42 [0.13, 0.70], baseline 0.67 [0.36, 0.92]
- all images, **n High = 23**: fine-tuned 0.70 [0.48, 0.88], baseline 0.83 [0.65, 0.96]

Critical-class recall (tuned rule, all / excl. 900+): erythema FT 0.54 / 0.48 vs baseline 0.59 / 0.55; edema 0.57 / 0.53 vs 0.56 / 0.50; **purulent 0.03 / 0.03 vs 0.30 / 0.31**; elevated infection 0.52 / 0.43 vs 0.58 / 0.48.

## Secondary: official test minus leaked images (n = 124, tuned rule)

Underpowered (16 elevated, **5 High-risk**, 4 purulent), intervals mostly 0.2 to 0.3 wide.

| head | subset | n | macro F1 FT | macro F1 baseline | critical AUROC FT | critical AUROC baseline |
|---|---|---|---|---|---|---|
| erythema | all | 118 | 0.62 [0.53, 0.71] | 0.60 [0.50, 0.69] | 0.72 [0.60, 0.83] | 0.73 [0.61, 0.83] |
| edema | all | 102 | 0.57 [0.46, 0.69] | 0.65 [0.54, 0.75] | 0.62 [0.48, 0.75] | 0.72 [0.60, 0.84] |
| exudate | all | 113 | 0.44 [0.31, 0.54] | 0.40 [0.30, 0.50] | 0.80 [0.67, 0.94] | 0.92 [0.80, 1.00] |
| infection | excl. 900+ | 113 | 0.65 [0.49, 0.78] | 0.61 [0.50, 0.73] | 0.72 [0.53, 0.90] | 0.75 [0.57, 0.91] |
| infection | all | 124 | 0.72 [0.59, 0.82] | 0.66 [0.55, 0.76] | 0.79 [0.62, 0.92] | 0.81 [0.67, 0.93] |

High-risk predicted elevated: 5/5 for both models (n High = 5; excl. 900+, n High = 2).
The secondary fine-tuned model's inner-val selection stopped at epoch 3, and it is weaker than the baseline on edema and purulent ranking (purulent AUROC diff -0.12 [-0.20, -0.04], on 4 purulent images).

## Source probe

Logistic regression predicting "ID 900+" (73/686) from image features, grouped 5-fold CV:
frozen pretrained AUROC **0.93 [0.88, 0.97]**, fine-tuned AUROC **0.92 [0.88, 0.95]**.
Fine-tuning does not remove source identity from the representation.

## What changed with the tuned decision rule

- Plain argmax had erythema macro F1 FT 0.64 vs baseline 0.60. With both models given an inner-val decision rule, the gap shrinks to +0.03 [-0.01, +0.07]. Part of the earlier gap was the baseline's threshold, not representation quality.
- The rule does not rescue purulent for the fine-tuned model. In 3 of 5 folds, inner-val (1 to 7 purulent images) chose alpha = 0, so the decision stays at argmax. The fine-tuned model ranks purulent no worse than the baseline (AUROC 0.76 vs 0.72), but its purulent probabilities are too low for this one-parameter rule to reach on a tiny inner-val. Phase 4 (calibration) and Phase 6 (rules that never let low confidence push toward "On track") should treat purulent as unreliable.
- Learned alphas vary widely across folds (0 to 0.95), another sign that about 88 inner-val images is a noisy basis for any decision rule.

## Decisions recorded

- Fine-tuned model carried forward (needed for Grad-CAM), with the tuned decision rule.
- Not done: retraining with new class weights (B) and multi-seed averaging (C).

## Notes for Phase 3

- After masking or inpainting text and overlays, rerun the ID 900+ source probe (frozen and fine-tuned features) and report whether the AUROC drops.
- The secondary-protocol model is undertrained (epoch 3). Grad-CAM figures should use the CV fold models on their own evaluation folds.
