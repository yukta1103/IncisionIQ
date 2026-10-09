# Phase 3: Explainability and shortcut audit

Reproduce (run sequentially; running two GPU jobs at once overflows 8 GB of VRAM):
```
python scripts/phase3_explain.py --config configs/phase2_convnext_tiny.yaml            # audit, original model, ~2 min
python scripts/phase2_train.py   --config configs/phase3_convnext_tiny_inpainted.yaml  # mitigation retrain, ~60 min
python scripts/phase2_eval.py    --config configs/phase3_convnext_tiny_inpainted.yaml  # ~10 min
python scripts/phase3_explain.py --config configs/phase3_convnext_tiny_inpainted.yaml  # audit, mitigated model
python scripts/phase3_compare.py                                                       # comparison.md
```
All before/after tables: `comparison.md`. Per-image data: `<model>/cam_overlay.parquet`, `<model>/occlusion.parquet`. Figure set: `figure_set.json`.

## Headline

- **The overlay shortcut was real but modest, and inpainting removes it.** Before mitigation, Grad-CAM for infection put 1.6x more mass on overlays than their area warrants, and removing overlays at test time lowered P(elevated) by 0.043 [0.028, 0.061] (0.079 on ID 900+ images). After retraining on inpainted images, that causal effect is gone (-0.006 [-0.014, +0.002], 0 decision flips).
- **Removing overlays does not remove the source.** The ID 900+ probe stays at AUROC 0.93 [0.88, 0.96] on frozen features and 0.89 [0.83, 0.94] on fine-tuned features (before: 0.93 and 0.92). The source is identifiable from the photographs themselves (patients, wound severity, framing, backgrounds), not from text. **The ID 900+ excluded results remain the primary honest estimate.**
- **Ranking performance is unchanged** (infection AUROC 0.77 [0.71, 0.82] excluding 900+, before and after; paired difference -0.004 [-0.029, +0.021]).
- **At the Phase 2 tuned decision rule, infection macro F1 is significantly lower** with the mitigated model: paired difference -0.046 [-0.083, -0.010] excluding 900+ (-0.048 [-0.077, -0.019] on all images). The mitigated model's rule calls more images elevated (141 vs 88 excluding 900+; false alarms 99 vs 52), mostly because one fold's inner-val chose a stronger prior correction. This is a threshold shift, not a change in ranking. The accompanying rise in High-risk recall has the same cause and is **not** attributed to the mitigation. Phase 4 replaces this rule with a recall-target operating point.

## Method

- **Grad-CAM** (pytorch-grad-cam) on the last ConvNeXt stage (12x12 map at 384 px input), fp32, target = the critical class of each head (erythema present, edema present, exudate purulent, infection elevated). **Every image is explained by the CV fold model that never trained on it.**
- **Overlay regions:** OCR text boxes plus orange redaction boxes, mapped into letterboxed model coordinates. CAM mass is measured over real image pixels only (letterbox padding excluded). 74 of 686 images have overlay regions.
- **CAM audit:** per overlay image and head, the share of CAM mass inside overlay regions vs the share of image area they cover. Excess = mass minus area (0 = no preference).
- **Causal check:** the same fold model scores each overlay image twice, as published and with overlays inpainted. Reported: mean change in P(critical class) and the number of argmax decision flips.
- **Mitigation:** overlays inpainted (OpenCV Telea, boxes dilated by 30% of their height) at train and test time, then the full Phase 2 protocol rerun unchanged (same folds, inner splits, seeds, candidate grid, decision rule; config `configs/phase3_convnext_tiny_inpainted.yaml` inherits everything else).
- CIs: 2,000 bootstrap resamples of same-patient groups.

## Results

### Before mitigation (Phase 2 model, original images)

| head | n | overlay area share | CAM mass on overlays | excess | dP(critical) when overlays removed | flips |
|---|---|---|---|---|---|---|
| erythema | 74 | 0.053 | 0.08 [0.05, 0.10] | +0.023 [+0.006, +0.044] | -0.016 [-0.030, -0.002] | 7 |
| edema | 74 | 0.053 | 0.08 [0.05, 0.10] | +0.023 [+0.001, +0.046] | -0.014 [-0.025, -0.005] | 4 |
| exudate | 74 | 0.053 | 0.06 [0.05, 0.08] | +0.010 [-0.006, +0.024] | -0.006 [-0.011, -0.002] | 3 |
| **infection** | 74 | 0.053 | **0.09 [0.06, 0.11]** | **+0.033 [+0.014, +0.052]** | **-0.043 [-0.061, -0.028]** | 4 |
| infection, ID 900+ only | 28 | 0.081 | 0.14 [0.10, 0.17] | +0.055 [+0.016, +0.094] | -0.079 [-0.119, -0.046] | 3 |

Overlays consistently push predictions toward the worse class. The effect is concentrated in ID 900+ images, where overlays are Russian clinical captions and redaction boxes.

### After mitigation (retrained on inpainted images)

| | before | after |
|---|---|---|
| infection: CAM excess on (former) overlay regions | +0.033 [+0.014, +0.052] | -0.031 [-0.044, -0.019] |
| infection: dP(elevated) when overlays removed | -0.043 [-0.061, -0.028], 4 flips | -0.006 [-0.014, +0.002], 0 flips |
| source probe AUROC, frozen features | 0.93 [0.88, 0.97] | 0.93 [0.88, 0.96] |
| source probe AUROC, fine-tuned features | 0.92 [0.88, 0.95] | 0.89 [0.83, 0.94] |
| infection AUROC, excl. 900+ (n = 613) | 0.77 [0.71, 0.82] | 0.77 [0.71, 0.82] |
| infection AUROC, all (n = 686) | 0.80 [0.75, 0.84] | 0.79 [0.74, 0.84] |
| infection macro F1, excl. 900+ (paired diff -0.046 [-0.083, -0.010]) | 0.66 [0.61, 0.71] | 0.62 [0.57, 0.66] |
| High-risk recall, excl. 900+ (n High = 12) | 0.42 [0.13, 0.70] | 0.67 [0.36, 0.92] |
| High-risk recall, all (n High = 23) | 0.70 [0.48, 0.88] | 0.83 [0.67, 0.96] |
| exudate macro F1, all | 0.43 [0.38, 0.48] | 0.47 [0.41, 0.52] |

Negative CAM excess after mitigation means the model now looks at inpainted regions less than their area, as expected for blank patches. The "after" causal check asks whether the mitigated model would still react if overlays reappeared; it essentially does not for infection, edema and exudate. Erythema moves slightly the other way (+0.016 [+0.003, +0.029]).

Other heads: erythema and edema AUROC change by at most 0.02, within the intervals. Full tables: `comparison.md`.

### Grad-CAM figures

`figures/convnext_tiny_384_gradcam_{1,2}.png` (before) and `figures/convnext_tiny_384_inpainted_gradcam_{1,2}.png` (after) show the same 12 official-test images, picked by a fixed rule: 2 High risk, 2 Medium, 2 purulent, 1 overlay image from ID 900+, 2 from other sources, 3 Low risk without overlays.
- On most images the infection and erythema maps sit on the wound.
- Before mitigation, the exudate and edema maps on 943.jpg spread over the Russian caption banner and the redaction box. After mitigation the infection map moves onto the wound, but P(elevated) on the two ID 900+ images rises to 0.97 and 0.98, consistent with the probe: the source is still recognizable.
- Maps are coarse (12x12 cells of 32 px): they highlight the wound region, not specific features like a suture line or a rim of redness.
- **Identifiability:** all 12 images were reviewed at full resolution. No faces, names, tattoos or jewelry. 451.jpg carried a platform account number in its watermark; all detected text and overlay regions are pixelated in the displayed figures (CAMs are still computed on the real model input). Attribution and license: `figures/ATTRIBUTION.md` (the figures are CC BY-SA 4.0 adaptations of SurgWound images).

## What the mitigation does not cover

- **Corner platform logos** (an estimated 39% of images, Phase 1) and **phone screenshot chrome** (status bars, thumbnail strips) are not detected and stay in the images.
- **Caption banners:** the text is inpainted, but the colored banner behind it can survive as a faint band (e.g. 937.jpg).
- **Source style:** the probe shows the 900+ source is identifiable without any overlay. No image-level mitigation can fix a label distribution that differs by source; the defensible responses are reporting the excluded estimate and, with more data, source-stratified validation.

## Corrections made during this phase

- **Orange-box detector false positives.** Reviewing every detection found 5 false positives among 37 images (a wooden floor, an orange blanket, a cloth edge, a floor patch and a region of skin next to a wound). The first mitigation run would have inpainted those areas, so it was stopped before finishing. The detector now requires the overlay's fixed shape (1.5 to 6% of the image, aspect 2.5 to 4.5). Phase 1 numbers were corrected (32 orange-box images, 67 with any detected overlay) and the conclusion is unchanged.
- **Inpainting mask uses a second OCR tier** (confidence >= 0.25 with >= 3 letters) to cover Russian captions read at confidence 0.29 to 0.44. All 11 images it adds were reviewed and are genuine overlay text.

## Decision recorded

**Model A (mitigated, inpainted inputs) is used for Phases 4 to 6.** It shows no measurable dependence on overlays and the same ranking as the original model. ID 900+ excluded numbers stay primary.

## Inference pipeline

`src/inference/pipeline.py` runs the same OCR + orange-box detection + inpainting on every incoming photo before the model sees it (it is not optional) and logs, per photo, whether any region was inpainted, how many regions, their area share and the OCR time. Only box coordinates are kept; OCR text is not stored, since it can contain personal data. On four test photos the online output was pixel-identical to the training-time inpainting. OCR adds about 0.2 to 1.7 s per photo on the RTX 4060.
