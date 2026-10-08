# IncisionIQ: explainable surgical wound assessment (work in progress)

Portfolio project: a multi-task image classifier for post-operative surgical wounds, built with the habits a regulated clinical product needs (patient-level splits, confidence intervals on every number, shortcut audits). **Not a medical device and not clinically validated.**

Status: Phase 1 (data audit) and Phase 2 (classifier) done. Calibration, explainability, report generation, the triage rules and the demo are still to come. This page is replaced by a full write-up in Phase 7.

## Data

SurgWound (Xu et al., *SurgWound-Bench: a benchmark for surgical wound diagnosis*, npj Digital Medicine 2026, doi:10.1038/s41746-026-02791-3), Hugging Face `xuxuxuxuxu/SurgWound`, CC BY-SA 4.0. 686 social-media images with expert labels.

## Evaluation protocol

- **Primary:** grouped 5-fold cross-validation over all 686 images, pooled out-of-fold predictions. Groups join images of the same patient (the official split is image-level but not patient-level; see `results/phase1/REPORT.md`).
- **Secondary:** official test split minus test images that have a same-patient partner in train/val, for rough comparability with the paper. Training never includes a test image's group partners.
- 95% confidence intervals come from bootstrap resampling of patient groups.

## Results so far (Phase 2)

**Fine-tuning a ConvNeXt-Tiny clearly helps only erythema, and only in ranking (critical-class AUROC 0.71 vs 0.64, difference +0.07 [+0.03, +0.12]). On every other head, and on macro F1 for all heads, it ties a logistic-regression baseline on frozen features.**

Infection risk (Low vs Elevated), grouped CV, tuned decision rule. The estimate excluding image IDs 900+ (a single source rich in severe cases) is the primary honest estimate:

| subset | n | n High-risk | macro F1 | AUROC (elevated) | High-risk recall |
|---|---|---|---|---|---|
| excluding IDs 900+ | 613 | 12 | 0.66 [0.61, 0.71] | 0.77 [0.71, 0.82] | 0.42 [0.13, 0.70] |
| all images | 686 | 23 | 0.69 [0.64, 0.73] | 0.80 [0.75, 0.84] | 0.70 [0.48, 0.88] |

Full tables: `results/phase2/REPORT.md`.

## Reproduce

All paths are relative to the repo root.
```
python -m venv --system-site-packages .venv   # or a plain venv, then install torch/torchvision cu121 wheels
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python scripts/phase1_audit.py   # downloads the data on first run
.venv/Scripts/python scripts/phase2_train.py
.venv/Scripts/python scripts/phase2_eval.py
```
