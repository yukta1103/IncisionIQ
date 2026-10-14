"""Demo checks: single deployed model, honest examples, privacy notices, no disk writes."""
import builtins
import json
import os

import pandas as pd
import pytest
from PIL import Image

from src.utils import ROOT, load_config

DEPLOY = json.loads((ROOT / "results" / "phase6" / "deployment.json").read_text(encoding="utf-8"))
EXAMPLES = ROOT / "src" / "app" / "examples"


def test_single_deployed_model_with_its_own_parameters():
    assert DEPLOY["deployed_fold"] == 0
    assert "ensemble" not in DEPLOY
    assert str(DEPLOY["deployed_fold"]) in DEPLOY["folds"]
    assert DEPLOY["ocr_max_side"] == 1024


def test_examples_are_held_out_by_the_deployed_fold():
    cfg = load_config(ROOT / DEPLOY["config"])
    fold = pd.read_csv(ROOT / cfg["results_dir"] / "splits.csv").set_index("image_name").cv_fold
    assert len(DEPLOY["examples"]) == 4
    for e in DEPLOY["examples"]:
        assert (EXAMPLES / e["image_name"]).exists()
        assert fold[e["image_name"]] == DEPLOY["deployed_fold"] == e["cv_fold"]
        assert e["official_split"] == "test"
    assert sorted(p.name for p in EXAMPLES.glob("*.jpg")) == sorted(e["image_name"] for e in DEPLOY["examples"])


def test_app_shows_demo_notice_and_privacy_text():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "src" / "app" / "app.py"), default_timeout=60).run()
    assert not at.exception
    assert any("Do not upload real patient photos" in e.value for e in at.error)
    assert any("not saved to disk" in c.value for c in at.caption)
    assert any("Surgeon rating for this photo" in c.value for c in at.caption)
    assert all("surgeon-rated" in o for o in at.selectbox[0].options)
    at.radio[0].set_value("Upload a photo").run()
    assert any("not a valid test" in c.value for c in at.caption)


@pytest.fixture(scope="module")
def predictor():
    cfg = load_config(ROOT / DEPLOY["config"])
    if not (ROOT / cfg["checkpoint_dir"] / cfg["name"] / "cv0.pt").exists():
        pytest.skip("checkpoints not available")
    from src.inference.pipeline import OverlayRemover, WoundPredictor

    return WoundPredictor(cfg, folds=[DEPLOY["deployed_fold"]], remover=OverlayRemover(max_side=DEPLOY["ocr_max_side"]))


def test_prediction_writes_nothing_and_reproduces_example_bands(predictor, monkeypatch):
    from src.triage.decide import attributes_from_probs

    real_open, real_os_open = builtins.open, os.open

    def no_write_open(file, mode="r", *a, **kw):
        assert not any(c in mode for c in "wax+"), f"write attempted: {file}"
        return real_open(file, mode, *a, **kw)

    def no_write_os_open(path, flags, *a, **kw):
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT), f"write attempted: {path}"
        return real_os_open(path, flags, *a, **kw)

    fold = DEPLOY["deployed_fold"]
    images = {e["image_name"]: Image.open(EXAMPLES / e["image_name"]).copy() for e in DEPLOY["examples"]}
    monkeypatch.setattr(builtins, "open", no_write_open)
    monkeypatch.setattr(os, "open", no_write_os_open)
    for e in DEPLOY["examples"]:
        res = predictor.predict(images[e["image_name"]], photo_id="upload", fold=fold)
        predictor.gradcam(res["clean_image"], "infection", 1, fold=fold)
        attrs = attributes_from_probs(res["probs_array"], DEPLOY["folds"][str(fold)], DEPLOY["band_rates"])
        assert attrs["infection"]["band"] == e["band_out_of_fold"], e["image_name"]
