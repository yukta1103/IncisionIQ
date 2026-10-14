"""IncisionIQ demo: photo + three questions -> attributes, Grad-CAM, grounded report, verdict.

Run from the repo root:  streamlit run src/app/app.py

- Every photo goes through OCR + inpainting before the model sees it (src/inference/pipeline.py).
- Every photo, example or upload, is scored by one model: CV fold 0 (chosen by fixed rule, not
  performance), with the decision parameters the cross-validation tested for that fold.
- The examples are fold 0 held-out images, so their results are honest out-of-fold predictions.
- Photos are processed in memory on the server running the app; they are never written to disk,
  and only the inpainting statistics are logged, never the photo or its content.
"""
import json
import sys
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.report.template import render  # noqa: E402
from src.triage.decide import attributes_from_probs  # noqa: E402
from src.triage.verdict import ON_TRACK, REVIEW, WATCH, PatientAnswers, photo_quality, verdict  # noqa: E402

EXAMPLE_DIR = Path(__file__).parent / "examples"
DEPLOY = json.loads((ROOT / "results" / "phase6" / "deployment.json").read_text(encoding="utf-8"))
LEVEL_STYLE = {REVIEW: ("#b42318", "#fef3f2"), WATCH: ("#b54708", "#fffaeb"), ON_TRACK: ("#067647", "#ecfdf3")}
STANDING_ADVICE = ("Whatever the result: contact your care team if you develop fever, spreading redness, new or increased "
                   "drainage, or worsening pain.")
FOLD = DEPLOY["deployed_fold"]
PARAMS = DEPLOY["folds"][str(FOLD)]
EXAMPLE_LABELS = {e["image_name"]: f"Example {i + 1}: surgeon-rated {e['infection_risk']} infection risk"
                  for i, e in enumerate(DEPLOY["examples"])}

st.set_page_config(page_title="IncisionIQ demo", page_icon="🩹", layout="centered")
st.markdown("""<style>
.block-container {max-width: 720px; padding-top: 1.2rem; padding-left: 1rem; padding-right: 1rem;}
.verdict {border-radius: 12px; padding: 14px 16px; margin: 8px 0 4px 0; border: 2px solid;}
.verdict h3 {margin: 0 0 4px 0;}
.small {font-size: 0.85rem; color: #555;}
</style>""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading models (first run only)...")
def load_predictor():
    from src.inference.pipeline import OverlayRemover, WoundPredictor

    return WoundPredictor.from_config(DEPLOY["config"], folds=[FOLD],
                                      remover=OverlayRemover(max_side=DEPLOY["ocr_max_side"]))


def describe(attr: str, a: dict) -> str:
    if a["uncertain"]:
        return "uncertain from this photo"
    if attr == "exudate":
        return {"none": "none visible", "non_purulent": "clear or bloody drainage may be visible",
                "purulent": "purulent drainage may be visible"}[a["value"]] + " (photo-based, unreliable)"
    return "likely present" if a["value"] == "present" else "not seen"


def cam_overlay(cam: np.ndarray, disp: np.ndarray) -> np.ndarray:
    from pytorch_grad_cam.utils.image import show_cam_on_image

    return show_cam_on_image(disp.astype(np.float32) / 255, cam, use_rgb=True)


st.title("IncisionIQ")
st.caption("Explainable surgical wound photo check. Portfolio demo, **not a medical device** and not clinically "
           "validated.")
st.error("**Demo only. Do not upload real patient photos.**")
st.caption("Your photo is processed in memory by the server running this app (your own computer if you run it "
           "locally, Streamlit Community Cloud on the public demo). It is not saved to disk, not logged, and not "
           "sent to any other service.")

# ---- 1. photo
st.subheader("1. Photo")
source = st.radio("Photo source", ["Example image", "Upload a photo", "Take a photo"], horizontal=True,
                  label_visibility="collapsed")
image, name = None, None
if source == "Example image":
    choice = st.selectbox("Example (official test split)", [e["image_name"] for e in DEPLOY["examples"]],
                          format_func=lambda n: EXAMPLE_LABELS.get(n, n))
    image = Image.open(EXAMPLE_DIR / choice)
    name = choice
    rating = next(e["infection_risk"] for e in DEPLOY["examples"] if e["image_name"] == choice)
    st.caption(f"Surgeon rating for this photo: **{rating}** infection risk (from SurgWound; the model does not "
               "see it). The examples mix agreements, a referral and a false alarm.")
elif source == "Upload a photo":
    up = st.file_uploader("Photo of the wound", type=["jpg", "jpeg", "png", "webp"])
    st.caption("Uploading images from the SurgWound dataset is not a valid test: the model trained on 80% of "
               "them. Use the examples instead; they come from the 20% it never saw.")
    if up is not None:
        image, name = Image.open(up), "upload"
else:
    shot = st.camera_input("Photo of the wound")
    if shot is not None:
        image, name = Image.open(shot), "camera"
if image is not None:
    image = ImageOps.exif_transpose(image).convert("RGB")
    st.image(image, width=260)

# ---- 2. questions
st.subheader("2. A few questions")
pain = st.slider("How bad is the pain at the wound right now? (0 = none, 10 = worst)", 0, 10, 2)
worse = st.radio("Is the pain getting worse?", ["No", "Yes"], horizontal=True) == "Yes"
fever = st.radio("Have you had a fever (38 °C / 100.4 °F or higher)?", ["No", "Yes"], horizontal=True) == "Yes"
drainage = st.radio("Is there fluid or pus coming from the wound?", ["No", "Yes"], horizontal=True) == "Yes"
st.caption("The pain-trend question is an addition to the original three so that worsening pain can be checked.")

if st.button("Check the wound", type="primary", use_container_width=True, disabled=image is None):
    predictor = load_predictor()
    with st.spinner("Removing text from the photo and running the model..."):
        result = predictor.predict(image, photo_id=name, fold=FOLD)
        attrs = attributes_from_probs(result["probs_array"], PARAMS, DEPLOY["band_rates"])
        prep = result["preprocess"]
        quality = photo_quality(*result["size"], prep["inpainted_area_frac"])
        v = verdict(attrs, PatientAnswers(pain=pain, pain_worsening=worse, fever=fever, drainage=drainage), quality)
        cam, disp = predictor.gradcam(result["clean_image"], "infection", 1, fold=FOLD)

    # ---- verdict
    color, bg = LEVEL_STYLE[v["level"]]
    st.markdown(f"<div class='verdict' style='border-color:{color}; background:{bg}'>"
                f"<h3 style='color:{color}'>{v['level']}</h3><div style='color:#1d2939'>{v['action']}</div></div>", unsafe_allow_html=True)
    st.markdown("**Why:**\n" + "\n".join(f"- {r}" for r in v["reasons"]))
    st.warning(STANDING_ADVICE)

    # ---- image findings
    st.subheader("Photo findings")
    band = attrs["infection"]["band"]
    rate = DEPLOY["band_rates"][band]
    st.markdown(f"**Infection risk group: {band}.** In validation, {round(100 * rate['rate'])} in 100 photos in this "
                f"group (95% CI {round(100 * rate['ci95'][0])} to {round(100 * rate['ci95'][1])}) were rated Medium or "
                f"High risk by surgeons.")
    st.markdown("\n".join([f"- Redness: {describe('erythema', attrs['erythema'])}",
                           f"- Swelling: {describe('edema', attrs['edema'])}",
                           f"- Drainage on the photo: {describe('exudate', attrs['exudate'])}. "
                           "The verdict uses your answer about drainage instead."]))
    if prep["inpainted"]:
        st.info(f"{prep['n_regions']} text or sticker region(s) were removed from the photo before analysis "
                f"({100 * prep['inpainted_area_frac']:.1f}% of the image), so the detected text cannot influence the result (small logos may remain).")

    c1, c2 = st.columns(2)
    c1.image(disp, caption="What the model saw (text removed, padded to a square)", use_column_width=True)
    c2.image(cam_overlay(cam, disp), caption="Grad-CAM for elevated infection risk", use_column_width=True)
    st.caption("The heat map highlights the wound region the model relies on. At 12x12 resolution it does not "
               "identify specific features, and it is not a clinical finding.")

    # ---- grounded report
    st.subheader("Report")
    st.write(render(attrs))
    st.caption("Generated only from the attributes above; nothing else is added.")

    with st.expander("Technical details"):
        st.markdown(f"- Model: `{result['model']}`. Every photo is scored by this one model, fold 0 of the 5-fold "
                    "cross-validation, chosen by a fixed rule (the first fold), not by performance. It uses the "
                    "decision thresholds the cross-validation tested for fold 0. It trained on 80% of SurgWound; the "
                    "examples come from the 20% it never saw, so their results are honest out-of-fold predictions.\n"
                    "- Risk-group rates are pooled over all five folds' held-out images (excluding IDs 900+).\n"
                    + f"- Photo preparation: {prep['n_regions']} region(s) inpainted, OCR {prep['seconds']:.1f} s.\n"
                    "- Confidence is shown as a risk group with its observed rate, not as a probability, because the "
                    "model's raw probabilities over-predict at the high end.")
else:
    if image is None:
        st.caption("Choose an example or add a photo to start.")

st.divider()
st.caption("Images: SurgWound dataset (Xu et al., npj Digital Medicine 2026), CC BY-SA 4.0. "
           "This demo does not give medical advice. If you are worried about your wound, contact your care team.")
