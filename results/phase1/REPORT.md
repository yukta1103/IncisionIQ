# Phase 1: Data audit

Reproduce with `python scripts/phase1_audit.py` (config `configs/phase1_audit.yaml`, seed 42).
Raw data: Hugging Face `xuxuxuxuxu/SurgWound`, CC BY-SA 4.0 (Xu et al., npj Digital Medicine 2026, doi:10.1038/s41746-026-02791-3).
Machine-readable results: `results/phase1/summary.json`, `class_counts.csv`. Manual review decisions: `configs/dedup_review.yaml`.

## 1. Pivot

5,600 rows (4,914 multiple-choice VQA + 686 report rows) pivot to **686 images x 8 attributes + 1 expert report**.
No conflicting answers, every answer is in its option list, all images are RGB JPEG.
Output: `data/processed/surgwound.parquet`, original JPEG bytes in `data/processed/images/`.

## 2. Is the official split image-level?

**By image name and by file bytes, yes.** 480 / 69 / 137 images, zero `image_name` overlap, zero byte-identical files across splits.

**By patient, no.** Visual review of pHash and DINOv2 candidates found the same patient or wound photographed more than once, often split across train and test (multi-photo social media posts, consecutive image IDs). Examples: 87, 88, 89, 90 (same knee, 2 train + 2 test); an ankle series 874 to 884 (train + test); 976/984 (val/test).

| Grouping rule | groups | images in groups | groups crossing splits | test images with a partner in train/val |
|---|---|---|---|---|
| verified only (24 groups) | 24 | 57 | 12 | **12** (8.8% of test) |
| verified + uncertain | 37 | 83 | 14 | 14 |
| conservative automatic (verified + uncertain + ID gap <= 3 with cosine >= 0.70 + any cosine >= 0.90) | 79 | 251 | 53 | 56 (an upper bound, many are false positives) |

Exact duplicates: one pair (119/124, both test). pHash alone is weak here: only 3 pairs at Hamming <= 8, and 1 of them is a false positive. Precision of the "adjacent ID and cosine >= 0.70" rule from manual review: roughly 80% above 0.80, dropping to about 25% near 0.74, so the verified list is a lower bound.

## 3. Class counts (all splits)

"Uncertain" never appears as an answer. Instead, **the question row is simply missing**. 92 to 98% of expert reports for those images describe the attribute as uncertain or unspecified (vs 29 to 47% for labeled images), so missing means Uncertain.

| attribute | classes (total, test) | missing (= Uncertain) |
|---|---|---|
| healing | Healed 406 (82), Not Healed 280 (55) | 0 |
| infection_risk | Low 573 (117), Medium 90 (15), **High 23 (5)** | 0 |
| urgency | Home Care 600 (121), Clinic Visit 68 (12), **Emergency 18 (4)** | 0 |
| erythema | Non-existent 469 (91), Existent 191 (40) | 26 |
| edema | Non-existent 473 (94), Existent 81 (21) | 132 |
| exudate | Non-existent 531 (109), Serous 36 (8), Sanguineous 29 (4), **Purulent 19 (3)**, **Seropurulent 11 (1)** | 60 |
| closure | Invisible 115 (19), Sutures 350 (68), **Staples 8 (1)**, **Adhesives 19 (4)** | 194 |
| location | Abdomen 112, Patella 35 (3), Ankle 72, Facial 66, Manus 35, Cervical 26 (4), Other 178 | 162 |

Bold = fewer than 20 examples. Full per-split tables: `class_counts.md`.
Val is tiny (69 images; 1 High-risk, 1 Emergency).

**Urgency is nearly a deterministic function of infection risk:** Low to Home Care 573/573; Medium to Clinic 64/90; High to Emergency 18/23.

## 4. Near-duplicates

Covered in section 2. Sheets: `dedup/phash_pairs_*.png`, `dedup/embed_pairs_*.png`, `dedup/adjacent_id_pairs_*.png`. Groups saved to `data/processed/groups.parquet` (one column per rule).

## 5. Image sizes and overlays

Width is 640 px for most images; median 640 x 853, short side < 384 px for 36 images, < 224 px for 5. Same distribution in all splits. Plot: `image_sizes.png`.

Overlays (automatic detection: easyocr Chinese+English pass, Russian+English pass, and a color detector for orange redaction boxes):

| overlay type | count | how measured |
|---|---|---|
| any detected text or orange box | 67 / 686 (9.8%) | automatic |
| text (captions, dates, phone-camera watermarks) | 47 | OCR, 24/24 sampled flags were real text |
| orange pixelated redaction boxes | 32 | color detector with a size/aspect filter; every detection reviewed (see correction below) |
| small corner platform logo | about 39% (14/36 sample, 95% CI 25 to 55%) | manual count on random unflagged sample, not detected automatically |
| captions/stickers OCR missed | about 8% of unflagged (3/36, CI 3 to 22%) | manual |

**Shortcut risk, confirmed at the data level:**
- Overlay rate vs infection risk: High 43% (10/23), Medium 14%, Low 8% (44/573). Orange boxes alone: High 30% (7/23, CI 16 to 51%) vs Low 3% (15/573, CI 2 to 4%).
- IDs 900 to 1005 (11% of images) contain 48% of all High-risk labels and 28 of 32 orange-box images. They carry Russian captions from what looks like one surgeon's educational account with severe cases ("severe necrotizing infection", "amputation at mid-thigh", "multiple fistulas"). A model can learn "orange box or Cyrillic caption means High risk".
- Some captions state the label outright, e.g. 76.jpg says "red, swollen and itchy" in Chinese.
- Faces are partially visible in some facial-region images (some are pixelated by the source, some are not).

**Correction (made in Phase 3).** The first version of this report counted 37 orange-box images and 72 images with any overlay. Reviewing every detection in Phase 3 showed 5 false positives (a wooden floor, an orange blanket, a cloth edge, a floor patch, and a region of skin next to a wound). The detector now requires the overlay's fixed shape (1.5 to 6% of the image, aspect 2.5 to 4.5); the numbers above are corrected. The conclusion is unchanged.

## 6. Decisions needed (options, not decisions)

### A. Grouping for evaluation
1. **Keep the official test split, remove leaked test images** (12 verified, or 14 with uncertain) from the final test score. Comparable to the paper, but a smaller test set (123 to 125).
2. **Keep the official split, move leaked train/val partners out of training** instead. Keeps all 137 test images, loses about 15 training images.
3. **Re-split by group** (official split discarded). Cleanest, but numbers are no longer comparable to the published benchmark.
4. Which grouping rule for 5-fold CV: verified only (risk: residual leakage), verified+uncertain, or conservative automatic (over-groups, 16-image largest group, safest). Over-grouping costs little here, so I lean conservative for CV, but it is your call.

### B. Uncertain (missing) labels
1. **Mask in the loss** (recommended by your spec). Uses all images for the other heads. The model is never asked to say "uncertain".
2. **Model Uncertain as a class**. Lets the system say "cannot tell", but "uncertain" here mostly means the photo lacks information (e.g. closure not visible), which is a photo-quality signal, not a wound finding.
3. Drop images with any missing label. Loses most data (location and closure are missing for 24 to 28%).

### C. Rare classes and heads
- **Closure:** Staples (8) cannot be learned or evaluated (1 test image). Options: merge Staples+Adhesives into "Other closure", or drop the head. Closure is also not clinically central for SSI.
- **Exudate:** Purulent 19 / Seropurulent 11 (1 test image). Options: collapse to 3 classes (None / Serous-Sanguineous / Purulent-any) or binary (None vs Present). Purulent-any is the clinically important SSI signal.
- **Infection risk:** High has 23 (5 test). Options: keep 3 classes and report High recall with a very wide CI; or binary Low vs Elevated (Medium+High, 113). Binary gives a usable CI.
- **Urgency:** nearly redundant with infection risk (see section 3). Options: drop the head and derive urgency from risk + rules in Phase 6; or keep it as a separate head knowing it adds almost no independent signal; or binary Home vs Not Home.
- **Location:** 7 classes plus 26% missing and "Other" is the largest class. Low clinical value for triage. Options: keep as an auxiliary head (may help the backbone), or drop.
- **Healing, erythema, edema:** fine as binary heads (edema has 81 Existent, OK but thin).

### D. Overlays and source shortcut
1. Mask or inpaint all detected overlays (text + orange boxes) at train and test time from the start, and still run the Phase 3 audit.
2. Train without masking first, then measure the shortcut in Phase 3 and mitigate (your current plan; gives a clean before/after).
3. Additionally report metrics with the IDs 900+ "source" stratum excluded, to show performance does not depend on it.
The corner logos are not detected automatically; I can add a template detector if you want them in the mask.

### E. Claims to agree on
- Report test numbers against the official split while being explicit that it leaks at the patient level, or redefine "test".
- The paper's benchmark is VQA with MLLMs, so our classifier numbers are not directly comparable to theirs either way.
