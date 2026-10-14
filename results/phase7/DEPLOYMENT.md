# Phase 7b: Deployment assessment for a free, CPU-only public demo

Nothing has been deployed. Platform limits were checked on 2026-10-14 from the sources at the end; both providers say their limits can change.

## What the demo needs (measured on this machine)

| item | size / cost |
|---|---|
| one fold checkpoint (fp32) | 107 MB (all 5: 535 MB; fp16 copies would be about 55 MB each) |
| EasyOCR models (detector 83 MB, Chinese 22 MB, Cyrillic 15 MB) | 115 MB, downloaded on first use |
| process memory, CPU only, 2 threads: Python + app imports | 369 MB |
| + EasyOCR readers loaded | 1,029 MB |
| + all 5 fold models loaded | 1,554 MB |
| peak during a prediction with Grad-CAM (5 models) | about 2.0 GB |
| latency, one model: OCR + inpainting + prediction | 4.8 s (OCR alone 4.5 s) |
| latency, one model: Grad-CAM | 1.7 s |
| latency, 5-model ensemble: prediction / Grad-CAM | 5.5 s / 3.3 s |

Memory was measured with the CUDA build of torch 2.5.1 running on the CPU. The CPU-only wheel a host would install is smaller, so these are upper bounds. A CPU-wheel measurement was not possible here (no package-index access from this environment). A single model with EasyOCR is estimated at 1.1 to 1.5 GB peak: the 1,029 MB baseline, plus about 110 MB of weights, plus activations.

## The two platforms

| | Hugging Face Spaces | Streamlit Community Cloud |
|---|---|---|
| free hardware | CPU Basic: 2 vCPU, 16 GB RAM, 50 GB non-persistent disk | about 0.078 to 2 cores, 690 MB to 2.7 GB memory, up to 50 GB storage (documented as of February 2024) |
| can a free account run this app? | **No, not as written.** The current docs list three SDKs (Gradio, Docker, static HTML; Streamlit now runs through Docker) and state that Gradio and Docker Spaces require a paid plan (PRO, $9/month) to create. Free accounts can host up to 2 Gradio Spaces on ZeroGPU, which would mean rewriting the UI in Gradio. | **Yes.** It deploys the existing `src/app/app.py` from a public GitHub repo. |
| fits in memory? | easily (16 GB) | 5 models: about 2.0 GB against a 2.7 GB cap, so it fits with little headroom. One model: about 1.1 to 1.5 GB, comfortable. |
| model weights | can live in the Space repo or a Hub model repo | must come from outside git (checkpoints are gitignored and over GitHub's 100 MB file limit): a GitHub Release asset or a Hugging Face Hub model repo, downloaded on first start |
| sleep | free hardware sleeps when unused | sleeps after 12 hours without traffic; any visitor can wake it |

## Recommendation: Streamlit Community Cloud, with a single model

Streamlit Community Cloud is the only one of the two that is free for this app as it stands, and it runs the existing Streamlit code unchanged. If paying for Hugging Face PRO were acceptable, CPU Basic would remove every memory concern, but the brief asks for free.

**A single model is not strictly needed for memory, but it is recommended:**
- **Headroom.** About 2.0 GB of 2.7 GB is close to the cap, the limits are from February 2024 and may change, and resources are shared. One model leaves room.
- **Cold start.** It downloads 107 MB of weights instead of 535 MB, plus the 115 MB of OCR models, on each wake from sleep (the disk is not persistent).
- **Latency.** Grad-CAM drops from 3.3 s to 1.7 s, on cores that may be slower than this machine's.
- **Honesty.** A single fold model uses its own thresholds, which the cross-validation actually ran. The 5-model ensemble with fold-averaged thresholds is a setting the cross-validation never evaluated (Phase 4 and 6 reports).

What a single model would change, and so needs your decision:
- **Uploads would be scored by one fold model (trained on 80% of the data) instead of the ensemble.** The README and app text would change to match.
- **The four examples need folds 1, 2 and 4** for honest out-of-fold scoring. To keep one model in memory, their attributes, band and Grad-CAM could be computed offline with the right fold model and stored as small files, with the verdict still computed live from the patient's answers. The alternative is loading the other fold models lazily, one at a time.

## Changes needed before any public deployment (not made)

1. **Privacy text.** The app says it "runs on this computer; the photo is not sent anywhere". On a hosted demo, the photo goes to the host's server. The text must change, and the page should ask people not to upload photos of real patients or identifiable photos.
2. **CPU wheels:** `torch==2.5.1+cpu` and `torchvision==0.20.1+cpu` from the PyTorch CPU index, in a deployment requirements file. Use `opencv-python-headless`, and drop the training-only packages (`anthropic`, `datasets`, `statsmodels`).
3. **Weights hosting and license.** Publishing the checkpoints distributes a model trained on CC BY-SA 4.0 data. The conservative choice is to publish them under CC BY-SA 4.0 with the SurgWound attribution (see `AUDIT.md`). Publishing is outward-facing and needs your approval.
4. **Preload and cache** EasyOCR and the model with `st.cache_resource` (already done for the model), and show a "waking up" message during the first download.

## Sources (checked 2026-10-14)

- Hugging Face, Spaces overview (hardware, paid-plan requirement for Gradio and Docker Spaces, sleep): https://huggingface.co/docs/hub/en/spaces-overview
- Hugging Face pricing (PRO $9/month, CPU Basic listed free): https://huggingface.co/pricing
- Streamlit, Manage your app (resource limits as of February 2024, 12-hour sleep): https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- Streamlit forum, resource-limits FAQ: https://discuss.streamlit.io/t/faq-this-app-has-gone-over-its-resource-limits/62973
