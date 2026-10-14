"""Phase 7: export the deployed model's weights for public hosting.

Writes dist/ (gitignored):
  incisioniq_fold0_v1.pt   state_dict of the CV fold 0 model (fp32, unchanged) plus a small
                           metadata dict; loadable with torch.load(weights_only=True)
  WEIGHTS_LICENSE.md       CC BY-SA 4.0 notice and SurgWound attribution
and records the file's SHA-256 in src/app/weights.json, which the app checks before loading,
together with the pinned URLs and checksums of the EasyOCR models (src/app/weights.py).

The training checkpoint also holds the training config and train/val/eval indices; only the
weights are exported.

Usage: python scripts/phase7_export_weights.py
Then upload both dist/ files as assets of the GitHub release `weights-v1` (see README).
"""
import hashlib
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utils import ROOT, load_config, save_json  # noqa: E402

FOLD = 0
TAG = "weights-v1"
FILENAME = "incisioniq_fold0_v1.pt"
REPO = "yukta1103/IncisionIQ"
# EasyOCR 1.7.2's models for our two passes (ch_sim+en, ru+en), from the EasyOCR project's versioned
# GitHub releases (Apache-2.0). SHA-256 of the extracted .pth files, computed from a fresh download.
OCR_MODELS = [
    {"filename": "craft_mlt_25k.pth", "url": "https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip",
     "sha256": "4a5efbfb48b4081100544e75e1e2b57f8de3d84f213004b14b85fd4b3748db17"},
    {"filename": "zh_sim_g2.pth", "url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/zh_sim_g2.zip",
     "sha256": "cb678fdef09d651e7763ca551ad790dc89f0b2e3d2a640484330e338fb574c7a"},
    {"filename": "cyrillic_g2.pth", "url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.6.1/cyrillic_g2.zip",
     "sha256": "48d0f3b58f28aa64651ab1032cc2d498c4de25135829668e87c14e7a07529f29"},
]
ATTRIBUTION = ("Trained on SurgWound (Xu et al., SurgWound-Bench: a benchmark for surgical wound diagnosis, "
               "npj Digital Medicine 2026, doi:10.1038/s41746-026-02791-3), CC BY-SA 4.0.")

LICENSE_MD = f"""# IncisionIQ model weights ({FILENAME})

ConvNeXt-Tiny multi-task wound model, grouped cross-validation fold 0, trained on inpainted images.
Code: https://github.com/{REPO} (MIT).

These weights are licensed under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/),
because they are derived from the SurgWound dataset. {ATTRIBUTION}

Portfolio project. Not a medical device and not clinically validated; do not use for patient care.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    dep = json.loads((ROOT / "results" / "phase6" / "deployment.json").read_text(encoding="utf-8"))
    assert dep["deployed_fold"] == FOLD
    cfg = load_config(ROOT / dep["config"])
    ck = torch.load(ROOT / cfg["checkpoint_dir"] / cfg["name"] / f"cv{FOLD}.pt", map_location="cpu", weights_only=False)
    out = {"state_dict": ck["state_dict"],
           "meta": {"model": cfg["name"], "backbone": cfg["backbone"], "cv_fold": FOLD,
                    "best_epoch": int(ck["best_epoch"]), "license": "CC BY-SA 4.0", "attribution": ATTRIBUTION,
                    "code": f"https://github.com/{REPO}"}}
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    path = dist / FILENAME
    torch.save(out, path)
    (dist / "WEIGHTS_LICENSE.md").write_text(LICENSE_MD, encoding="utf-8")
    spec = {"filename": FILENAME, "url": f"https://github.com/{REPO}/releases/download/{TAG}/{FILENAME}",
            "sha256": sha256(path), "size_bytes": path.stat().st_size, "license": "CC BY-SA 4.0",
            "release_tag": TAG, "cv_fold": FOLD, "ocr_models": OCR_MODELS}
    save_json(spec, ROOT / "src" / "app" / "weights.json")
    print(json.dumps(spec, indent=1))


if __name__ == "__main__":
    main()
