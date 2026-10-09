# IncisionIQ: explainable surgical wound assessment (work in progress)

Portfolio project: a multi-task image classifier for post-operative surgical wounds, built with the habits a regulated clinical product needs (patient-level splits, confidence intervals on every number, shortcut audits). **Not a medical device and not clinically validated.**

Status: Phases 1 to 4 done (data audit, classifier, explainability and shortcut audit, calibration and operating point). Report generation, the triage rules and the demo are still to come. This page is replaced by a full write-up in Phase 7.

## Data

SurgWound (Xu et al., *SurgWound-Bench: a benchmark for surgical wound diagnosis*, npj Digital Medicine 2026, doi:10.1038/s41746-026-02791-3), Hugging Face `xuxuxuxuxu/SurgWound`, CC BY-SA 4.0. 686 social-media images with expert labels.

## Evaluation protocol

- **Primary:** grouped 5-fold cross-validation over all 686 images, pooled out-of-fold predictions. Groups join images of the same patient (the official split is image-level but not patient-level; see `results/phase1/REPORT.md`).
- **Secondary:** official test split minus test images that have a same-patient partner in train/val, for rough comparability with the paper. Training never includes a test image's group partners.
- 95% confidence intervals come from bootstrap resampling of patient groups.

## Results so far (Phase 2)

**Fine-tuning improves erythema ranking (AUROC +0.07 [+0.03, +0.12]). Macro F1 differences are not significant on any head, and the baseline has higher recall on High-risk and purulent cases.**

Infection risk (Low vs Elevated), grouped CV, tuned decision rule. The estimate excluding image IDs 900+ (a single source rich in severe cases) is the primary honest estimate:

| subset | n | n High-risk | macro F1 | AUROC (elevated) | High-risk recall |
|---|---|---|---|---|---|
| excluding IDs 900+ | 613 | 12 | 0.66 [0.61, 0.71] | 0.77 [0.71, 0.82] | 0.42 [0.13, 0.70] |
| all images | 686 | 23 | 0.69 [0.64, 0.73] | 0.80 [0.75, 0.84] | 0.70 [0.48, 0.88] |

Full tables: `results/phase2/REPORT.md`.

## Shortcut audit (Phase 3)

Inpainting removed a measurable text-overlay shortcut (overlay effect on P(elevated) went from 0.043 to 0.006) with no change in ranking (AUROC 0.77). The image source remains identifiable from the photos themselves (frozen-feature probe AUROC 0.93 before and after masking), so ID 900+ excluded results remain primary.

At the Phase 2 tuned decision rule, infection macro F1 is lower with the mitigated model (paired difference -0.046 [-0.083, -0.010], excluding ID 900+). Ranking is unchanged (AUROC difference -0.004 [-0.029, +0.021]); the drop is a threshold shift (more images called elevated), so Phase 4 sets the operating point by a recall target. The mitigated model is used from Phase 4 on. Details: `results/phase3/REPORT.md`, `results/phase3/comparison.md`.

## Operating point and confidence bands (Phase 4)

Infection risk is reported as one of three bands, each shown with its observed rate of Elevated risk, not as a raw probability (temperature scaling did not improve calibration, and high probabilities over-predict). Grouped CV, out-of-fold, excluding IDs 900+ (n = 613):

| band | share of images | observed Elevated rate |
|---|---|---|
| low concern | 45% | 4% [2, 7] |
| uncertain, refer for review | 24% | 12% [7, 17] |
| high concern, flag | 30% | 29% [22, 36] |

With "uncertain" and "high concern" both going to a clinician, **0.86 [0.78, 0.93] of Elevated images are flagged or referred, at a clinician workload of about 55 per 100 images (54.8 [50.3, 58.9])**, against an Elevated prevalence of 84 of 613 (14%). 2 of the 12 High-risk images fall in the low-concern band.

The recall target used to set the flag threshold on each fold's inner-validation slice (0.8) was not met out-of-fold (0.64 [0.54, 0.75] for the flag alone). Each slice holds only 8 to 18 Elevated images, and the same slice was already used for model selection, so it gives optimistic estimates; the referral band is what brings the system to 0.86. Details: `results/phase4/REPORT.md`.

## Design choices backed by the numbers

- **Drainage comes from the patient, not the image.** The image model's purulent predictions are treated as unreliable: across grouped CV the Phase 2 model catches 1 of 30 purulent wounds (recall 0.03 [0.00, 0.11]) and the mitigated model used from Phase 4 on catches 3 of 30 (0.10 [0.00, 0.21]); the frozen baseline catches 9 of 30. The triage verdict therefore takes drainage from the patient's own answer, and the image model's exudate output is shown for information only.
- **Macro F1 is not the triage objective.** The infection operating point is chosen by a recall target on Elevated risk, with the false-alarm cost shown at each target (Phase 4).

## Limitations (so far)

- **Small dataset:** 686 images; the rarest classes have 30 or fewer examples (purulent exudate 30, High infection risk 23), so their estimates have wide intervals.
- **Social-media photos,** not photos taken in a home-monitoring app; selection bias toward cases people chose to post.
- **One image source dominates the severe cases** (IDs 900+) and is identifiable from the photos themselves.
- **Overlays the mitigation does not remove:** small corner platform logos (an estimated 39% of images), phone screenshot UI (status bars, buttons, thumbnail strips), and the colored banners behind captions (the caption text is inpainted, the banner can remain as a faint band).
- **Not clinically validated and not a medical device.**

## Reproduce

All paths are relative to the repo root.
```
python -m venv --system-site-packages .venv   # or a plain venv, then install torch/torchvision cu121 wheels
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python scripts/phase1_audit.py   # downloads the data on first run
.venv/Scripts/python scripts/phase2_train.py
.venv/Scripts/python scripts/phase2_eval.py
```
