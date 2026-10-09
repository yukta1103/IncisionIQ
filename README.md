# IncisionIQ: explainable surgical wound assessment (work in progress)

Portfolio project: a multi-task image classifier for post-operative surgical wounds, built with the habits a regulated clinical product needs (patient-level splits, confidence intervals on every number, shortcut audits). **Not a medical device and not clinically validated.**

Status: Phase 1 (data audit), Phase 2 (classifier) and Phase 3 (explainability and shortcut audit) done. Calibration, explainability, report generation, the triage rules and the demo are still to come. This page is replaced by a full write-up in Phase 7.

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

Text and redaction overlays measurably pushed the infection head toward "elevated": inpainting them at test time lowered P(elevated) by 0.043 [0.028, 0.061]. Retraining on inpainted images removes that dependence (-0.006 [-0.014, +0.002]) with unchanged ranking (AUROC 0.77 excluding IDs 900+). It does not remove the source signal: image features still identify the ID 900+ source with AUROC 0.93, so the excluded estimate stays primary. Details: `results/phase3/REPORT.md`.

## Design choices backed by the numbers

- **Drainage comes from the patient, not the image.** The image model's purulent predictions are treated as unreliable: across grouped CV it catches 1 of 30 purulent wounds (recall 0.03 [0.00, 0.11]; the frozen baseline catches 9 of 30). The triage verdict therefore takes drainage from the patient's own answer, and the image model's exudate output is shown for information only.
- **Macro F1 is not the triage objective.** The infection operating point is chosen by a recall target on Elevated risk, with the false-alarm cost shown at each target (Phase 4).

## Reproduce

All paths are relative to the repo root.
```
python -m venv --system-site-packages .venv   # or a plain venv, then install torch/torchvision cu121 wheels
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python scripts/phase1_audit.py   # downloads the data on first run
.venv/Scripts/python scripts/phase2_train.py
.venv/Scripts/python scripts/phase2_eval.py
```
