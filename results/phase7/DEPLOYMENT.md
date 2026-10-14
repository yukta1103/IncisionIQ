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

## Still needed before any public deployment (not done)

1. **Re-measure memory on the target platform** (Linux, CPU wheel) and watch for resource-limit restarts.
2. **CPU wheels:** a deployment requirements file with `torch==2.5.1+cpu` and `torchvision==0.20.1+cpu` from the PyTorch CPU index, `opencv-python-headless`, and without the training-only packages (`anthropic`, `datasets`, `statsmodels`).
3. **Weights hosting:** publishing the fold 0 checkpoint distributes a model trained on CC BY-SA 4.0 data, so publish it under CC BY-SA 4.0 with the SurgWound attribution. Publishing is outward-facing and needs your approval.
4. **A cold-start message** while EasyOCR and the checkpoint download after the app wakes from sleep.

## Sources (checked 2026-10-14)

- Streamlit, Manage your app (resource limits "as of February 2024", behavior over limits, 12-hour sleep): https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- Streamlit forum, resource-limits FAQ: https://discuss.streamlit.io/t/faq-this-app-has-gone-over-its-resource-limits/62973
- Streamlit forum, runtime and memory limits (staff reply: 1 GB guaranteed, up to about 3 GB depending on load; older thread): https://discuss.streamlit.io/t/is-there-a-runtime-limit-other-than-memory-limit-on-streamlit-cloud-apps/61358
- Third-party 2026 summaries repeating the 690 MB to 2.7 GB range, or quoting 1 GB: https://fastero.com/blog/streamlit-community-cloud-vs-paid-hosting-options , https://livemy.app/blog/deploy-streamlit-app
- Hugging Face, Spaces overview (hardware, paid-plan requirement, sleep): https://huggingface.co/docs/hub/en/spaces-overview
- Hugging Face pricing (PRO $9/month, CPU Basic listed free): https://huggingface.co/pricing
