# Phase 7c: Pre-push audit

Last run on 2026-10-14 over every commit of local `main`, and separately over `origin/main` as last fetched.

## Status of the remote: action needed

**GitHub `main` is at dc75d13** (the first Phase 7 commit). It was pushed on 2026-10-14 at about 15:41, before the Phase 7 decisions to redact and to remove 111.jpg. The commits after e905730, which those decisions treated as unpushed, are therefore public, and they contain:
- `src/app/examples/111.jpg`, with its burned-in caption (a diagnosis and procedure, no personal identifier);
- the un-redacted VLM caption transcriptions for 8 images, in `results/phase5/vlm/vlm_outputs.parquet`, `vlm/reports.parquet` and `markdown_validation_export.md`;
- the first version of this file, which described both.

**Local `main` has been rewritten** from 0863bd6 onward (bfb2b83 and everything before it are unchanged), so it has diverged from GitHub. Nothing has been pushed. Getting the clean history onto GitHub needs a force-push (`git push --force-with-lease origin main`), which needs your approval. Even then:
- GitHub can keep serving the old commits by SHA until it garbage-collects them;
- any existing clones or forks keep them;
- GitHub Support can be asked to purge cached views.

## Results on local `main` (18 commits)

| check | result |
|---|---|
| any file under `data/` | none |
| `.env` in any commit | none; no API key appears in any file |
| un-pixelated figures | none; the four removed blobs no longer exist, and each Phase 3 Grad-CAM figure has one (pixelated) version |
| `src/app/examples/111.jpg` | **in no commit** |
| VLM caption transcriptions (original-script text and their quoted translations, decoded from every parquet version) | **none**; all 224 distinct text blobs scanned |
| Chinese or Cyrillic text outside `.py` files | none (the `.py` matches are OCR language settings and regex ranges) |
| platform account number from 451.jpg | none |
| EXIF / metadata in demo examples | none |
| `.claude/launch.json` | in 2 commits (a local Streamlit launch command, no secrets); untracked and gitignored since Phase 7 |

Images in history: plots without patient pixels, the 4 pixelated Grad-CAM figures, the Phase 6 examples 714, 315 and 282 (no detected text; removed from the tree in Phase 7 but kept in history, as only 111 was to be purged), and the Phase 7 examples 79, 411, 237 and 521.

## What was done

- **Redaction:** in 8 free-text reports the VLM had quoted and translated captions that the OCR missed. Those quotations are now "[caption text redacted]".
  - The rule is in `scripts/phase7_redact_vlm_captions.py`, which contains no caption text: it changes only report lines that contain Chinese or Cyrillic characters, then checks that no report still contains any.
  - The downstream files were regenerated. `metrics.json`, `comparison.md` and the validation results are byte-identical.
  - The same rule was applied to every historical version of the three files.
- **111.jpg** was removed from every commit, and the descriptions of its caption and of the transcriptions were removed from earlier versions of this file.
- **Examples** were replaced by a fixed rule (see `src/app/examples/ATTRIBUTION.md`).
- **License:** MIT for code (`LICENSE`); dataset-derived content is CC BY-SA 4.0 (README).

The VLM's own inferences about the wounds (for example the likely procedure, judged from the wound itself) are not transcriptions and were kept.
