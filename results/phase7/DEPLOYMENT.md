# Phase 7b: Deployment assessment for a free, CPU-only public demo

Nothing has been deployed. Platform limits were last checked on **2026-10-14** from the sources at the end; both providers say their limits can change without notice.

## Decided

- **One model everywhere** (local and hosted): the CV fold 0 model, chosen by fixed rule (the first fold), not by performance. It uses the decision parameters the cross-validation tested for fold 0 (`results/phase6/deployment.json`, `deployed_fold`). The four demo examples are fold 0 held-out images, so their results are out-of-fold.
- **Privacy in the app:**
  - A visible "Demo only. Do not upload real patient photos." notice.
  - Privacy text that holds both locally and hosted: the photo is processed in memory by the server running the app, and is not saved to disk, not logged and not sent to any other service.
  - Streamlit keeps uploads and camera shots in memory, and the pipeline never writes the photo. `tests/test_app.py` runs the full path (OCR, inpainting, prediction, Grad-CAM) with every file-write call trapped.
  - Only inpainting statistics are logged, and uploads are labeled "upload", never with the file name or an image hash.
  - `.streamlit/config.toml` turns off Streamlit usage statistics and caps uploads at 10 MB.

## OCR resolution cap for the demo: 1024 px

OCR, not the model, sets peak memory. It runs on a downscaled copy of the photo, and the boxes are mapped back to full resolution for inpainting. Training and evaluation used a 1280 px long side (`MAX_SIDE` in `src/data/ocr.py`, unchanged). The demo uses **1024 px** (`ocr_max_side` in `deployment.json`).

**Effect on the 686 dataset images** (`scripts/phase7_ocr_cap_check.py --cap 1024`, results in `ocr_cap_1024.json`). OCR was re-run at 1024 px and, as a run-to-run control, at 1280 px, on every image larger than 1024 px (smaller images are unaffected by construction). Images whose mask changed were re-scored by their out-of-fold model with that fold's parameters.

| | images |
|---|---|
| larger than 1024 px | 206 of 686 |
| inpainting mask differs at all | 32 (mostly small box-edge shifts; median mask IoU 0.95) |
| number of inpainted regions differs | 12 (113 regions in total at 1280 px, 115 at 1024 px) |
| a region lost entirely | 796.jpg (1 region to 0, so its text stays in the photo) |
| **infection band changes** | **1**: 788.jpg, low concern to uncertain (towards review, not away from it) |
| redness, swelling or drainage changes | 0 |

## What the demo needs (measured on this machine, CPU only, 2 threads, fold 0 model, OCR cap 1024 px)

| item | measurement |
|---|---|
| fold 0 checkpoint (fp32) | 107 MB |
| EasyOCR models (detector 83 MB, Chinese 22 MB, Cyrillic 15 MB) | 115 MB, downloaded on first use |
| memory with imports, EasyOCR and fold 0 loaded | about 0.85 to 1.1 GB |
| steady state after predictions | about 1.3 GB (1.6 GB at the 1280 px cap) |
| peak, 480 to 1138 px photos | 1.35 to 1.45 GB |
| peak, 1080 x 1440 photo | 1.92 GB (2.58 GB at the 1280 px cap) |
| **peak, largest photos tested (1440 x 1440; 1152 x 2048)** | **2.08 GB**; 1.48 GB |
| latency: OCR + inpainting + prediction, then Grad-CAM | 2.6 to 12 s, then 0.6 to 2.4 s |

These numbers come from the CUDA build of torch 2.5.1 running on the CPU, on Windows. A Linux host with the CPU-only wheel will differ but could not be measured here (no package-index access). OCR-only peaks for one large photo were 1.57 to 1.60 GB at 1280 px, 1.22 to 1.37 GB at 1024 px and 1.08 to 1.23 GB at 800 px.

## The two platforms (checked 2026-10-14)

| | Hugging Face Spaces | Streamlit Community Cloud |
|---|---|---|
| free hardware | CPU Basic: 2 vCPU, 16 GB RAM, 50 GB non-persistent disk | 0.078 to 2 cores, **690 MB minimum to 2.7 GB maximum memory**, up to 50 GB storage. The docs still date these limits to February 2024. |
| can a free account run this app? | **No, not as written.** The docs list Gradio, Docker and static SDKs (Streamlit runs through Docker) and say that Gradio and Docker Spaces need a paid plan (PRO, $9/month). Free accounts can host up to 2 Gradio Spaces on ZeroGPU, which would mean rewriting the UI in Gradio. | **Yes.** It deploys `src/app/app.py` from a public GitHub repo. |
| fits in memory? | easily | **Not guaranteed.** With the 1024 px cap the peak is 2.08 GB, about 0.6 GB under the 2.7 GB maximum, but the steady state (about 1.3 GB) is still above the 690 MB guaranteed minimum. The docs say an app over its limits "may slow down from throttling or become nonfunctional". |
| model weights | Space repo or a Hub model repo | from outside git (checkpoints are gitignored and over GitHub's 100 MB file limit): a GitHub Release asset or a Hub model repo, downloaded on first start |
| sleep | free hardware sleeps when unused | after 12 hours without traffic; any visitor can wake it |

## Recommendation

**Streamlit Community Cloud, with the fold 0 model and the 1024 px OCR cap.** It is the only free option that runs the app as written. The cap brings the worst measured peak from 2.58 GB to 2.08 GB at the cost of one band change in 686 images. The remaining risk is the shared-resource floor: Streamlit guarantees only 690 MB, so under load the app could be throttled or restarted. If that happens in practice, Hugging Face PRO ($9/month, CPU Basic with 16 GB) removes the problem. Porting to Gradio on free ZeroGPU is not recommended: it means a UI rewrite, and that free tier is GPU-quota-based, not a CPU host.

## Model weights: hosting proposal

The fold 0 checkpoint is gitignored. `scripts/phase7_export_weights.py` exports a weights-only file:
- `dist/incisioniq_fold0_v1.pt`: 111 MB, fp32, tensors identical to the training checkpoint (tested), with no training indices or config. It loads with `torch.load(weights_only=True)`.
- `dist/WEIGHTS_LICENSE.md`: the license and attribution notice.
- The file's SHA-256 is recorded in `src/app/weights.json`.

| | GitHub Release asset (recommended) | Hugging Face model repo |
|---|---|---|
| accounts | the existing GitHub repo | needs a Hugging Face account |
| limits | 2 GiB per asset; public download URL | large files via Git LFS/Xet; public download URL |
| license notice | release notes plus the `WEIGHTS_LICENSE.md` asset | a model card with `license: cc-by-sa-4.0` metadata |
| download in the app | plain HTTPS, no extra package | plain HTTPS (`resolve/<commit>/...`) or `huggingface_hub` |
| fit here | weights sit next to the code they belong to; nothing new to maintain | better discoverability; a second place to keep in sync |

**Recommendation: a GitHub Release `weights-v1`** on `yukta1103/IncisionIQ`, with the two `dist/` files as assets, **licensed CC BY-SA 4.0** (derived from SurgWound) with the attribution in the release notes. The code stays MIT.

**At startup** (`src/app/weights.py`), the app:
- looks in the cache (`~/.cache/incisioniq`, or `INCISIONIQ_CACHE`), then in a local `dist/` export;
- otherwise downloads from the release URL in `weights.json`;
- verifies the SHA-256 before use. A mismatch deletes the download and stops the app, so an unverified file is never loaded.

The model is loaded with `weights_only=True`, so the file cannot run code. `st.cache_resource` keeps the loaded model in memory. The cache survives restarts but not a fresh container (Community Cloud disk is not persistent), so a cold start downloads the file again. Tests cover checksum match, rejection of a tampered file, and caching.

## EasyOCR models

**How EasyOCR fetches them by default** (version 1.7.2, from its source):
- On the first `easyocr.Reader(...)`, it downloads ZIP files from the EasyOCR project's GitHub releases (JaidedAI/EasyOCR) into `~/.EasyOCR/model`, or `EASYOCR_MODULE_PATH`.
- It unzips them and checks an MD5.
- It uses `urlretrieve`, with no timeout and no retry.

On Streamlit Community Cloud the disk is not persistent, so this would repeat on every cold start.

**What the app does instead:** the three models our two OCR passes need are pinned in `src/app/weights.json`, each with its versioned release URL and our own SHA-256 of the extracted file. `src/app/weights.py`:
- downloads them with a 60 s timeout and 3 retries;
- verifies each checksum before moving the file into place;
- caches them in `~/.cache/incisioniq/easyocr`.

`OverlayRemover` then runs EasyOCR with `download_enabled=False`, pointed at that directory, so EasyOCR never downloads anything itself. These are EasyOCR's unmodified files, fetched from EasyOCR's releases (Apache-2.0); nothing is re-hosted.

| measured here (CPU) | |
|---|---|
| files | craft_mlt_25k (detector) 79 MB, zh_sim_g2 20 MB, cyrillic_g2 14 MB; 113 MB unzipped |
| cold start, downloading all three | 14 s and 229 s in two runs on this connection; the network is the variable |
| loading both readers from cache | 3.1 to 3.8 s |
| memory during reader start-up | about 1.16 GB peak, the same cold or warm: the download streams to disk and adds no memory. This is below the 2.08 GB prediction peak. |

**Remaining risk:** if the EasyOCR project ever removed those release files, the app would stop at start-up with a clear error rather than run without OCR. The fix would be to mirror the three files as assets of our own release, keeping their Apache-2.0 notice, and change the URLs in `weights.json`.

## Dependencies on Streamlit Community Cloud

- **`src/app/requirements.txt`** is the deployment file. Community Cloud reads the dependency file next to the entrypoint before the root one; the root `requirements.txt` stays the training environment.
- **CPU-only torch:** torch 2.5.1+cpu and torchvision 0.20.1+cpu are pinned by **direct wheel URL plus SHA-256** (Linux x86_64, CPython 3.12, checked against the PyTorch CPU index on 2026-10-14), so no CUDA build can be installed. Direct URLs work the same under uv, which Community Cloud tries first, and under pip.
- **One version conflict fixed:** streamlit 1.35.0 requires numpy below 2, and opencv-python-headless 4.13 requires numpy 2 or later. The deploy file pins **numpy 1.26.4** and **opencv-python-headless 4.10.0.84**, which accepts numpy 1.26. Locally the training env had installed both despite the conflict.
- **No system packages:** grad-cam 1.5.7 and EasyOCR both use `opencv-python-headless`, so no `packages.txt` is needed.
- **Python: 3.12**, chosen in the deploy dialog. The torch wheels are for 3.12 only.

## Deploying (manual steps)

1. **Create the weights release** (one time, outward-facing, so you do it). The files are already exported in `dist/`; re-run `python scripts/phase7_export_weights.py` if it is missing, and check that it prints the same `sha256` as `src/app/weights.json`. Then:
   ```
   gh release create weights-v1 dist/incisioniq_fold0_v1.pt dist/WEIGHTS_LICENSE.md --repo yukta1103/IncisionIQ --title "Model weights v1 (CC BY-SA 4.0)" --notes "Fold 0 ConvNeXt-Tiny wound model used by the demo. Licensed CC BY-SA 4.0 (derived from SurgWound, Xu et al., npj Digital Medicine 2026, doi:10.1038/s41746-026-02791-3). Not a medical device. SHA-256: see src/app/weights.json."
   ```
   You can also do this on GitHub: Releases, then Draft a new release, tag `weights-v1`, and attach both files. The URL must end up as `https://github.com/yukta1103/IncisionIQ/releases/download/weights-v1/incisioniq_fold0_v1.pt`, and the repo must be public.
2. **Check the asset** before deploying:
   ```
   curl -sL https://github.com/yukta1103/IncisionIQ/releases/download/weights-v1/incisioniq_fold0_v1.pt | sha256sum
   ```
   It must print the `sha256` in `src/app/weights.json`.
3. **Create the app** on https://share.streamlit.io: sign in with GitHub, then Create app, then "Deploy a public app from GitHub":
   - Repository: `yukta1103/IncisionIQ`
   - Branch: `main`
   - Main file path: `src/app/app.py`
   - App URL: any free subdomain
   - Advanced settings: Python version **3.12**; no secrets needed.
4. **Deploy and wait.** The first build installs about 1 GB of packages (several minutes). The first visit then downloads about 230 MB of model files (wound model and OCR models), shown as "Loading models...".
5. **Run the live checklist below.**

## Live checklist (after deploying)

The Windows test environment cannot prove the Linux build, so check the live app:
- [ ] **Build log:** no resolver errors; it lists `torch-2.5.1+cpu` and no `nvidia-*` packages.
- [ ] **Examples, no symptoms** (pain 2, all answers "No"), each with the standing advice under the verdict:
  - [ ] Example 1 (surgeon-rated Low): **On track**, low concern
  - [ ] Example 2 (surgeon-rated Medium): **Review recommended**, high concern
  - [ ] Example 3 (surgeon-rated Low): **Watch**, uncertain
  - [ ] Example 4 (surgeon-rated Low): **Review recommended**, high concern
- [ ] **Override:** Example 1 with fever set to "Yes" gives **Review recommended**.
- [ ] **One upload:** "Upload a photo" with `tests/fixtures/synthetic_caption.jpg` (a drawn image, no patient pixels). It must give a verdict and show **"3 text or sticker region(s) were removed from the photo"** (about 10.5% of the image), and the "What the model saw" image must have no caption. The region count can differ by one on Linux; the notice must appear.
- [ ] **Technical details** says `convnext_tiny_384_inpainted (fold 0)`.
- [ ] **Demo notice** "Demo only. Do not upload real patient photos." is visible at the top.
- [ ] **Manage app, then logs:** no tracebacks and no "checksum mismatch". If the app shows "Oh no" or restarts on a large photo, it hit the memory limit (see above).

## Sources (checked 2026-10-14)

- Streamlit, Manage your app (resource limits "as of February 2024", behavior over limits, 12-hour sleep): https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- Streamlit forum, resource-limits FAQ: https://discuss.streamlit.io/t/faq-this-app-has-gone-over-its-resource-limits/62973
- Streamlit forum, runtime and memory limits (staff reply: 1 GB guaranteed, up to about 3 GB depending on load; older thread): https://discuss.streamlit.io/t/is-there-a-runtime-limit-other-than-memory-limit-on-streamlit-cloud-apps/61358
- Third-party 2026 summaries repeating the 690 MB to 2.7 GB range, or quoting 1 GB: https://fastero.com/blog/streamlit-community-cloud-vs-paid-hosting-options , https://livemy.app/blog/deploy-streamlit-app
- Hugging Face, Spaces overview (hardware, paid-plan requirement, sleep): https://huggingface.co/docs/hub/en/spaces-overview
- Hugging Face pricing (PRO $9/month, CPU Basic listed free): https://huggingface.co/pricing
