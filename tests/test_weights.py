"""Published weights: identical to the training checkpoint, verified by checksum, cached."""
import hashlib

import pytest
import torch

from src.app import weights
from src.utils import ROOT

EXPORT = ROOT / "dist" / weights.SPEC["filename"]
TRAINING = ROOT / "checkpoints" / "phase3" / "convnext_tiny_384_inpainted" / "cv0.pt"


def test_spec_points_at_a_release_asset_with_a_checksum():
    assert weights.SPEC["url"].startswith("https://github.com/yukta1103/IncisionIQ/releases/download/")
    assert len(weights.SPEC["sha256"]) == 64 and weights.SPEC["license"] == "CC BY-SA 4.0"


@pytest.mark.skipif(not (EXPORT.exists() and TRAINING.exists()), reason="weights not available locally")
def test_export_matches_training_checkpoint_and_spec():
    assert weights.sha256(EXPORT) == weights.SPEC["sha256"]
    exp = torch.load(EXPORT, weights_only=True, map_location="cpu")
    ref = torch.load(TRAINING, weights_only=False, map_location="cpu")["state_dict"]
    assert exp["state_dict"].keys() == ref.keys()
    assert all(torch.equal(exp["state_dict"][k], ref[k]) for k in ref)
    assert exp["meta"]["license"] == "CC BY-SA 4.0" and exp["meta"]["cv_fold"] == 0


def test_download_verifies_and_caches(tmp_path, monkeypatch):
    src = tmp_path / "remote.bin"
    src.write_bytes(b"pretend weights")
    spec = {"filename": "w.bin", "url": src.as_uri(), "sha256": hashlib.sha256(b"pretend weights").hexdigest()}
    monkeypatch.setenv("INCISIONIQ_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(weights, "ROOT", tmp_path)  # no local dist/ export
    p = weights.weights_path(spec)
    assert p == tmp_path / "cache" / "w.bin" and p.read_bytes() == b"pretend weights"
    src.unlink()  # second call must come from the cache, not the network
    assert weights.weights_path(spec) == p


def test_download_with_wrong_checksum_is_rejected(tmp_path, monkeypatch):
    src = tmp_path / "remote.bin"
    src.write_bytes(b"tampered")
    spec = {"filename": "w.bin", "url": src.as_uri(), "sha256": "0" * 64}
    monkeypatch.setenv("INCISIONIQ_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(weights, "ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        weights.weights_path(spec)
    assert not (tmp_path / "cache" / "w.bin").exists() and not (tmp_path / "cache" / "w.part").exists()


def test_zipped_ocr_model_is_extracted_and_verified(tmp_path):
    import zipfile

    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("m.pth", b"ocr weights")
    good = hashlib.sha256(b"ocr weights").hexdigest()
    p = weights.fetch(archive.as_uri(), "m.pth", good, tmp_path / "ocr", zip_member="m.pth")
    assert p.read_bytes() == b"ocr weights" and sorted(x.name for x in p.parent.iterdir()) == ["m.pth"]
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        weights.fetch(archive.as_uri(), "x.pth", "0" * 64, tmp_path / "bad", zip_member="m.pth")
    assert list((tmp_path / "bad").iterdir()) == []


def test_ocr_models_are_pinned():
    names = sorted(m["filename"] for m in weights.SPEC["ocr_models"])
    assert names == ["craft_mlt_25k.pth", "cyrillic_g2.pth", "zh_sim_g2.pth"]
    assert all(m["url"].startswith("https://github.com/JaidedAI/EasyOCR/releases/download/") and len(m["sha256"]) == 64
               for m in weights.SPEC["ocr_models"])
