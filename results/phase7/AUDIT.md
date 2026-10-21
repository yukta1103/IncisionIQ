# Phase 7c: Pre-push audit

Last run on 2026-10-14 over every commit of local `main` before the first push to the recreated repo.

## Status of the remote

- **Old repo:** the commits that held the un-redacted material (pushed on 2026-10-14, before the redaction decisions) were removed from GitHub by deleting the repo. It was recreated empty under the same name; `git ls-remote origin` returned nothing before the push.
- **Clean history pushed:** local `main` (rewritten from the Phase 5 report commit, now c6a3b85, onward) was pushed with a normal `git push -u origin main`, with no force. The first pushed commit is now d29c46c (adcf027 when pushed; see the next point), and `origin/main` matched local `main` afterwards. Later fixes are normal new commits on top.
- **Stray merges aborted:** before the push, two merges of the old remote-tracking branch into local `main` were started outside this work (most likely `git pull` or GitHub Desktop). Neither was committed; both were aborted with `git merge --abort`. The stale `origin/main` tracking ref was then deleted and the old objects purged from the local object store, so they could not be pushed.
- **Commit metadata rewritten afterwards (2026-10-20):** the `Co-Authored-By` trailers were removed from every commit message and the history was force-pushed, so all commit hashes changed. File contents did not change: the tree of the last commit before the rewrite (5979349) is identical to its rewritten counterpart (3aef965). Hashes in this file refer to the current history.
- **Not recallable:** copies of the old commits made before the deletion (clones, forks, caches).

## Results on local `main`

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

Images in history: plots without patient pixels, the 4 pixelated Grad-CAM figures, the Phase 6 examples 714, 315 and 282 (no detected text; removed from the tree in Phase 7 but kept in history, as only 111 was to be purged), the first Phase 7 examples 237 and 521 (same checks; replaced but kept in history), 268.jpg (a child's neck and the back of the head, no face or text; an example in the pushed commit d29c46c, replaced afterwards by a normal commit, so it stays in history), and the final examples 79, 66, 411 and 30.

## What was done

- **Redaction:** in 8 free-text reports the VLM had quoted and translated captions that the OCR missed. Those quotations are now "[caption text redacted]".
  - The rule is in `scripts/phase7_redact_vlm_captions.py`, which contains no caption text: it changes only report lines that contain Chinese or Cyrillic characters, then checks that no report still contains any.
  - The downstream files were regenerated. `metrics.json`, `comparison.md` and the validation results are byte-identical.
  - The same rule was applied to every historical version of the three files.
- **111.jpg** was removed from every commit, and the descriptions of its caption and of the transcriptions were removed from earlier versions of this file.
- **Examples** were replaced by a fixed rule (see `src/app/examples/ATTRIBUTION.md`).
- **License:** MIT for code (`LICENSE`); dataset-derived content is CC BY-SA 4.0 (README).

The VLM's own inferences about the wounds (for example the likely procedure, judged from the wound itself) are not transcriptions and were kept.
