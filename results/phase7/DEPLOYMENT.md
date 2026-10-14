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

## What the demo needs (measured on this machine, CPU only, 2 threads)

| item | measurement |
|---|---|
| fold 0 checkpoint (fp32) | 107 MB |
| EasyOCR models (detector 83 MB, Chinese 22 MB, Cyrillic 15 MB) | 115 MB, downloaded on first use |
| memory: Python, Streamlit, torch and app imports | 641 MB |
| + EasyOCR readers | 915 MB |
| + fold 0 model | 1,109 MB |
| steady state after the first prediction | about 1,600 MB |
| **peak during OCR, 640 px photos** | **1.4 to 1.8 GB** |
| **peak during OCR, 1080 x 1440 photo** (OCR runs at up to 1280 px) | **2.58 GB** |
| latency, 640 px photo: OCR + inpainting + prediction / Grad-CAM | 3.1 to 4.2 s / 0.6 s |
| latency, 1080 x 1440 photo | 9.8 s / 2.4 s |

These numbers come from the CUDA build of torch 2.5.1 running on the CPU, on Windows. A Linux host with the CPU-only wheel will differ, probably downward, but this could not be measured here (no package-index access). **OCR, not the model, sets peak memory**: the five-model ensemble added only about 525 MB, while one OCR pass on a large photo adds about 950 MB.

## The two platforms (checked 2026-10-14)

| | Hugging Face Spaces | Streamlit Community Cloud |
|---|---|---|
| free hardware | CPU Basic: 2 vCPU, 16 GB RAM, 50 GB non-persistent disk | 0.078 to 2 cores, **690 MB minimum to 2.7 GB maximum memory**, up to 50 GB storage. The docs still date these limits to February 2024. |
| can a free account run this app? | **No, not as written.** The docs list Gradio, Docker and static SDKs (Streamlit runs through Docker) and say that Gradio and Docker Spaces need a paid plan (PRO, $9/month). Free accounts can host up to 2 Gradio Spaces on ZeroGPU, which would mean rewriting the UI in Gradio. | **Yes.** It deploys `src/app/app.py` from a public GitHub repo. |
| fits in memory? | easily | **Not guaranteed.** Steady state (about 1.6 GB) is above the 690 MB guaranteed minimum, and a large photo (2.58 GB) comes within 0.1 GB of the maximum. The docs say an app over its limits "may slow down from throttling or become nonfunctional". |
| model weights | Space repo or a Hub model repo | from outside git (checkpoints are gitignored and over GitHub's 100 MB file limit): a GitHub Release asset or a Hub model repo, downloaded on first start |
| sleep | free hardware sleeps when unused | after 12 hours without traffic; any visitor can wake it |

## Recommendation

**Streamlit Community Cloud is still the only free option that runs the app as written, but OCR memory is a blocker to fix before deploying.** Two ways forward, which need your decision:

1. **Cap the photo size before OCR** (for example a 1024 px long side for uploads), then confirm offline that the inpainted regions and infection bands on the 686 dataset images are unchanged, or report what changes. This changes the preprocessing pipeline, so it needs that check, and peak memory needs re-measuring afterwards. It is the cheapest fix.
2. **Pay for Hugging Face PRO** ($9/month) and use CPU Basic (16 GB) with a Docker Space. Memory stops being a concern, but the demo is no longer free.

The alternative of porting to Gradio on free ZeroGPU is not recommended: it means a UI rewrite, and the free tier is GPU-quota-based, not a CPU host.

## Still needed before any public deployment (not done)

1. **Fix the memory risk** (above) and re-measure on the target platform.
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
