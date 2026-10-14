# Phase 7c: Pre-push audit

Run on 2026-10-14 over every commit reachable from any ref (`git rev-list --all`: local `main` at the Phase 7 commit, `origin/main` at e905730). Reflog and stash are empty apart from the 9 local reflog entries since the Phase 4 history rewrite.

**Already public:** `origin/main` is at e905730 (Phase 5 scoring code), not d98d023 as earlier notes assumed. It includes the pixelated Phase 3 Grad-CAM figures and `results/phase5/{template_reports,template_claims}.parquet`, `metrics.json`, `tables.md` and `extractor_validation.csv`. Everything checked below is clean in that pushed part.

## Results

| check | result |
|---|---|
| any file under `data/` in any commit | **none** |
| `.env` (or any `.env*`) in any commit | **none**. The only matches for `ANTHROPIC_API_KEY` are the docstring in `scripts/phase5_vlm.py` describing the file format; `sk-ant` never appears. |
| un-pixelated figures | **none.** The four removed blobs (528b8d3, 0c1856c, f40b752, 78eb01e) no longer exist in the object store. Each Phase 3 figure has exactly one version in history, the pixelated one. |
| image files in history | plots only (confusion matrices, histograms, reliability and operating-point curves, which hold no patient pixels), the 4 pixelated Grad-CAM figures, and the 4 demo examples in `src/app/examples/` (see below) |
| platform account number from 451.jpg | not present in any text file in history |
| Cyrillic or Chinese text in any `.md/.csv/.json/.py/.yaml` | one file: `results/phase5/markdown_validation_export.md` (see below) |
| URLs, @handles, 7+ digit numbers in docs | only Creative Commons, Anthropic docs and privacy-article links |
| EXIF / metadata in the demo examples | none (0 EXIF tags, no extra info chunks) |
| `.claude/launch.json` | removed from the index and `.claude/` gitignored. It remains in unpushed commit c41cb9c and holds only a local Streamlit launch command. |

## Two things to decide before pushing

### 1. Caption text transcribed by the VLM (unpushed: `results/phase5/vlm/vlm_outputs.parquet`, `vlm/reports.parquet`, `markdown_validation_export.md`)

OCR plus inpainting missed some captions, and the VLM read them in its free-text reports, in 8 of 686 images (19, 20, 32, 85, 617, 718, 946, 978). The transcribed text was short captions about post-operative timing and the wound. **There are no names, handles, account numbers or locations.**

This also means some caption text reached the VLM provider despite the inpainting step. Text the OCR detects is removed, but text it misses is not. The README's data-handling section now says so.

Options:
- (a) **Push as is** (recommended). The text is not identifying, and it is already public in the SurgWound images themselves.
- (b) Redact the quoted caption strings in those three files before pushing. The commits are unpushed, so this needs a rewrite of local history (squashing or amending the unpushed commits), which needs your authorization.

Separately, 10 free-text reports include crisis-line resources (the VLM judged the wound might be self-inflicted). These hold no identifying information.

### 2. Demo example 111.jpg keeps its caption (unpushed)

111.jpg is committed as the dataset original. Its burned-in Chinese caption gives a diagnosis and procedure ([caption text redacted]) and [caption text redacted], and a faint platform watermark sits in the corner. That is health information but not identity, and the image is public in SurgWound. However, the Phase 3 figures pixelate detected text, and this example does not.

It is kept deliberately: it shows the inpainting step working on a real caption (3 regions, 9.8% of the image). Options:
- (a) keep it, and say in `src/app/examples/ATTRIBUTION.md` that the caption is part of the original image;
- (b) replace it with a captioned test-split image whose text holds no diagnosis;
- (c) drop it and keep 3 examples.

Options (b) and (c) only change unpushed commits if they are made before the first push, and that needs a local history rewrite to keep the file out of public history.

## Proposed license

- **Code** (`src/`, `scripts/`, `tests/`, `configs/`): **MIT.** It is permissive and short, and it does not conflict with CC BY-SA material kept alongside it, because the two cover separate files. Apache-2.0 also works if an explicit patent grant matters to the startup. Both are fine for a portfolio.
- **Dataset-derived material** (the demo examples, the pixelated Grad-CAM figures, per-image outputs and features in `results/`, and model weights if they are ever published): **CC BY-SA 4.0**, with attribution to Xu et al. 2026, as `ATTRIBUTION.md` already states for the examples and figures. ShareAlike applies to adaptations of the images. Treating weights and per-image outputs as covered is the conservative reading; whether they legally count as adaptations is unsettled.
- Proposed mechanics: a `LICENSE` file with MIT for the code, plus a short "Licenses" note in the README naming the CC BY-SA 4.0 paths. Not added yet, pending your choice.

This is a practical proposal, not legal advice.
