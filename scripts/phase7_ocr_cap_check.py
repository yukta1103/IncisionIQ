"""Phase 7: does a smaller OCR resolution cap change the preprocessing or the predictions?

The demo runs OCR on a copy whose long side is at most `ocr_max_side` (boxes are mapped
back to full resolution for inpainting). Training and evaluation used 1280 px. A lower cap
saves memory on a free host; this script measures what it changes on all 686 images:

- OCR is re-run at the new cap and, as a control for run-to-run noise, at 1280, on every
  image whose long side exceeds the new cap (smaller images are unaffected by construction).
- An image "changes" if its inpainting mask (kept OCR boxes plus orange boxes, as in
  training) differs from the 1280 control mask.
- Every changed image is re-scored by its out-of-fold model (the CV fold that never trained
  on it) with that fold's decision parameters, from both masks, and the attributes and
  infection band are compared.

Usage: python scripts/phase7_ocr_cap_check.py --cap 960
Writes results/phase7/ocr_cap_<cap>.json and prints a summary.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.inpaint import inpaint_image, keep_text_box  # noqa: E402
from src.data.ocr import MAX_SIDE, ocr_image  # noqa: E402
from src.eval.metrics import softmax  # noqa: E402
from src.inference.pipeline import OCR_LANG_PASSES, WoundPredictor  # noqa: E402
from src.data.labels import HEAD_NAMES  # noqa: E402
from src.triage.decide import attributes_from_probs  # noqa: E402
from src.utils import ROOT, load_config, save_json  # noqa: E402

KEEP = (0.5, 2, 0.25, 3)  # keep_text_box parameters, as in training and the pipeline


def mask(boxes, w, h, dilate_frac=0.3, min_pad=3):
    m = np.zeros((h, w), dtype=bool)
    for x0, y0, x1, y1 in boxes:
        pad = max(min_pad, int(dilate_frac * (y1 - y0)))
        m[max(0, int(y0) - pad):min(h, int(y1) + pad), max(0, int(x0) - pad):min(w, int(x1) + pad)] = True
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, required=True)
    args = ap.parse_args()
    import easyocr

    dep = json.loads((ROOT / "results" / "phase6" / "deployment.json").read_text(encoding="utf-8"))
    cfg = load_config(ROOT / dep["config"])
    proc = ROOT / cfg["processed_dir"]
    orange = json.loads((proc / "orange_boxes.json").read_text(encoding="utf-8"))
    fold = pd.read_csv(ROOT / cfg["results_dir"] / "splits.csv").set_index("image_name").cv_fold
    gpu = torch.cuda.is_available()
    readers = [easyocr.Reader(list(langs), gpu=gpu, verbose=False) for langs in OCR_LANG_PASSES]

    def boxes_at(im, side, name):
        dets = [d for r in readers for d in ocr_image(r, im, side)]
        return [d["bbox"] for d in dets if keep_text_box(d, *KEEP)] + orange.get(name, [])

    names = sorted(p.name for p in (proc / "images").glob("*.jpg"))
    rows = []
    for n in names:
        im = ImageOps.exif_transpose(Image.open(proc / "images" / n)).convert("RGB")
        if max(im.size) <= args.cap:
            continue
        ref, new = boxes_at(im, MAX_SIDE, n), boxes_at(im, args.cap, n)
        mr, mn = mask(ref, *im.size), mask(new, *im.size)
        rows.append({"image_name": n, "size": im.size, "n_ref": len(ref), "n_new": len(new),
                     "area_ref": float(mr.mean()), "area_new": float(mn.mean()),
                     "mask_iou": float((mr & mn).sum() / max(1, (mr | mn).sum())) if (mr | mn).any() else 1.0,
                     "changed": bool((mr != mn).any()), "_ref": ref, "_new": new})
    del readers

    pred = WoundPredictor(cfg, remover=object())  # all five folds; OCR is done above
    changed = [r for r in rows if r["changed"]]
    for r in changed:
        im = Image.open(proc / "images" / r["image_name"])
        k = int(fold[r["image_name"]])
        out = {}
        for tag in ("ref", "new"):
            x = pred._input(inpaint_image(im, r[f"_{tag}"]))
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=pred.device == "cuda"):
                o = pred.models[k](x)
            probs = {h: softmax(o[h].float().cpu().numpy())[0] for h in HEAD_NAMES}
            out[tag] = attributes_from_probs(probs, dep["folds"][str(k)], dep["band_rates"])
        r["band_ref"], r["band_new"] = out["ref"]["infection"]["band"], out["new"]["infection"]["band"]
        r["attrs_same"] = all(out["ref"][h]["value"] == out["new"][h]["value"]
                              and out["ref"][h]["uncertain"] == out["new"][h]["uncertain"]
                              for h in ("erythema", "edema", "exudate"))
    for r in rows:
        r.pop("_ref"), r.pop("_new")

    summary = {
        "cap": args.cap, "reference_cap": MAX_SIDE, "n_images": len(names),
        "n_above_cap": len(rows), "n_mask_changed": len(changed),
        "n_regions_ref": int(sum(r["n_ref"] for r in rows)), "n_regions_new": int(sum(r["n_new"] for r in rows)),
        "n_images_region_count_changed": int(sum(r["n_ref"] != r["n_new"] for r in rows)),
        "n_band_changed": int(sum(r["band_ref"] != r["band_new"] for r in changed)),
        "n_other_attributes_changed": int(sum(not r["attrs_same"] for r in changed)),
        "rows": rows,
    }
    save_json(summary, ROOT / "results" / "phase7" / f"ocr_cap_{args.cap}.json")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
    for r in changed:
        print(r["image_name"], r["size"], r["n_ref"], "->", r["n_new"], f"iou {r['mask_iou']:.2f}",
              r["band_ref"], "->", r["band_new"], "" if r["attrs_same"] else "(other attributes differ)")


if __name__ == "__main__":
    main()
