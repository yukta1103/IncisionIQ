# Phase 6: Verdict rules and demo

Reproduce:
```
python scripts/phase6_build_deployment.py   # decision parameters + check that they reproduce the evaluated system
python scripts/phase6_verdict_eval.py       # verdict levels on out-of-fold predictions
python -m pytest tests -q                   # 45 tests: every verdict rule, plus the demo checks in tests/test_app.py
streamlit run src/app/app.py                # the demo (models load on first use)
```

## Verdict rules (`src/triage/verdict.py`)

Explicit rules, checked in order. Every triggered rule adds a plain-English reason.

**Review recommended** (contact the care team today) if any of:
- fever reported,
- pain getting worse,
- pain 7 or higher,
- the photo is in the **high-concern** infection band,
- drainage reported and the photo is not in the low-concern band.

**Watch** (the care team reviews the photo; recheck within 24 to 48 hours) if no Review rule applies and any of:
- the photo is in the **uncertain** band (the Phase 4 referral band),
- drainage reported,
- pain 4 to 6,
- the photo can't be judged reliably (short side under 300 px, or more than 15% of it covered by removed text or stickers).

**On track** only if none of the above apply.

Design choices, as agreed:
- **The image enters only through the infection band** from the flag-or-refer operating point, so a low-confidence image can raise the verdict (uncertain band, poor photo) but never lower it to On track.
- **Drainage comes from the patient's answer.** The image's exudate output is shown for information only.
- **Fever or worsening pain override a low-concern image band** (2 of 12 High-risk images fall in that band).
- **Added question:** "Is the pain getting worse?" (yes/no). The original three inputs (pain 0 to 10, fever, drainage) cannot express a trend, so this fourth question was needed for the worsening-pain override.
- Thresholds (pain 7 and 4, 300 px, 15%) are product choices, not learned. They are stated in code and tested.

## What the levels mean (out-of-fold, no symptoms reported)

| subset | verdict | share of images | surgeon-rated Elevated | High-risk images |
|---|---|---|---|---|
| excl. 900+ (n = 613) | On track | 45% | 4% [2, 7] | 2 of 12 |
| excl. 900+ | Watch | 24% | 12% [7, 17] | 2 of 12 |
| excl. 900+ | Review recommended | 30% | 29% [22, 36] | 8 of 12 |
| all (n = 686) | On track | 42% | 4% [2, 6] | 2 of 23 |
| all | Watch | 23% | 13% [8, 18] | 2 of 23 |
| all | Review recommended | 35% | 33% [27, 40] | 19 of 23 |

With no symptoms the levels are the Phase 4 bands, so Watch plus Review route 0.86 [0.78, 0.93] of Elevated images (excl. 900+) to a clinician. SurgWound has no patient answers, so the symptom rules cannot be evaluated on data; they can only move a verdict up.

## Consistency checks

- **Decision parameters reproduce the evaluated system:** feeding the stored out-of-fold logits through `src/triage/decide.py` with each image's fold parameters gives the Phase 5 attributes for 686 of 686 images.
- **The full upload path reproduces it for the demo examples:** original file, then OCR + inpainting, then the fold 0 model gives the evaluated band for all four examples (`tests/test_app.py`).
- **One model everywhere (Phase 7 change).** The demo first scored uploads with the 5-model ensemble and fold-averaged thresholds, a setting the cross-validation never evaluated; the ensemble had also seen each dataset image in 4 of its 5 models. It now scores every photo with the **fold 0 model** (chosen by fixed rule, the first fold, not by performance) and the parameters the cross-validation tested for fold 0.

## Demo (`src/app/app.py`)

Streamlit, centered layout capped at 720 px, tested at 375 px phone width (no horizontal scroll; images stack vertically). The flow:
1. **Photo:** one of four examples (official test split, held out by fold 0, chosen by the fixed rule in `select_examples`: the lowest-ID image that is surgeon Low and predicted low concern, surgeon Elevated and predicted high concern, predicted referral band, and surgeon Low but predicted high concern, excluding images of children after a by-eye check; each is labeled with its surgeon rating; `src/app/examples/`, CC BY-SA attribution included), an upload, or the phone camera. A visible notice says the demo is for demonstration only and asks people not to upload real patient photos.
2. **Questions:** pain 0 to 10, pain getting worse, fever, drainage.
3. **Result:**
   - the verdict card with its reasons,
   - the infection risk group with its observed rate and CI (no raw probabilities),
   - redness, swelling and drainage as "likely present / not seen / uncertain",
   - a notice when text or stickers were removed,
   - the processed image next to the Grad-CAM for elevated infection risk,
   - the grounded report,
   - technical details (which model and thresholds were used, and why).
- **OCR + inpainting runs on every photo before the model sees it**, as in training; when text is removed the user is told so. (The examples were chosen to have no detected text, so this notice shows only for uploads.)
- **Photos stay in memory.** They are processed by the server running the app (the user's own computer when run locally) and are never written to disk, logged or sent to another service; `tests/test_app.py` traps file writes during the full prediction path.

Verified (Phase 7, Streamlit AppTest) with no symptoms: example 1 (79.jpg, surgeon Low) gives **On track**, example 2 (66.jpg, surgeon Medium) **Review recommended**, example 3 (411.jpg, surgeon Low) **Watch**, and example 4 (30.jpg, surgeon Low) **Review recommended**, a false alarm. Each shows the standing advice. Phase 6 also checked phone width (375 px) and the fever override in the browser.

No server errors.

## Limitations

- The symptom rules and thresholds are not validated against outcomes; SurgWound has no patient-reported data or follow-up.
- The demo model is fold 0 alone, trained on 80% of the data. Per-fold flag thresholds range from 0.08 to 0.48, so another fold would draw the bands differently; the displayed band rates are pooled over all five folds.
- Photos taken by patients at home differ from the social-media images the model was trained on. There is no photo-quality model beyond the size and overlay checks.
- Not a medical device and not clinically validated.
