"""Phase 3: Grad-CAM figures and overlay shortcut audit for one trained model.

Every image is explained by the CV fold model that never saw it in training.

Outputs (results/phase3/<model name>/):
  cam_overlay.parquet   per overlay image and head: CAM mass on overlay boxes, box area
  occlusion.parquet     per overlay image and head: P(critical) on original vs inpainted input
  shortcut_summary.json group-bootstrap CIs for the above
  gradcam_*.png         fixed figure set (same images for every model)

Usage: python scripts/phase3_explain.py --config configs/phase2_convnext_tiny.yaml
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from pytorch_grad_cam.utils.image import show_cam_on_image
from torchvision.transforms import v2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.dataset import build_transforms, load_images  # noqa: E402
from src.data.inpaint import overlay_boxes  # noqa: E402
from src.data.labels import CRITICAL_CLASS, HEAD_NAMES, HEADS, encode_labels  # noqa: E402
from src.eval.metrics import softmax  # noqa: E402
from src.explain.gradcam import box_mask, content_mask, gradcam_maps, mass_fraction, to_letterbox  # noqa: E402
from src.models.multitask import MultiTaskNet  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402

FIGURE_SET_FILE = ROOT / "results" / "phase3" / "figure_set.json"


def choose_figure_set(df, lab, has_overlay, seed) -> list[str]:
    """Fixed, rule-based pick from the official test split, written once and reused
    for every model so before/after figures show the same images."""
    if FIGURE_SET_FILE.exists():
        return json.loads(FIGURE_SET_FILE.read_text())["images"]
    rng = np.random.default_rng(seed)
    test = df.split.to_numpy() == "test"
    risk = df.infection_risk.to_numpy()
    src = lab.source_900plus.to_numpy() == 1
    pools = [
        ("High risk", test & (risk == "High"), 2),
        ("Medium risk", test & (risk == "Medium") & ~has_overlay, 2),
        ("purulent exudate", test & (lab.exudate.to_numpy() == 2), 2),
        ("overlay, ID 900+", test & has_overlay & src, 1),
        ("overlay, other source", test & has_overlay & ~src, 2),
        ("Low risk, no overlay", test & (risk == "Low") & ~has_overlay, 3),
    ]
    chosen, why = [], {}
    for label, mask, k in pools:
        cand = [n for n in df.image_name[mask] if n not in chosen]
        for n in rng.choice(cand, size=min(k, len(cand)), replace=False):
            chosen.append(str(n))
            why[str(n)] = label
    save_json({"rule": [p[0] for p in pools], "images": chosen, "category": why}, FIGURE_SET_FILE)
    return chosen


def load_fold_model(cfg, k, device):
    ck = torch.load(ROOT / cfg["checkpoint_dir"] / cfg["name"] / f"cv{k}.pt", weights_only=False, map_location=device)
    model = MultiTaskNet(cfg["backbone"], {h: len(HEADS[h]["classes"]) for h in HEAD_NAMES}, pretrained=False).to(device)
    model.load_state_dict(ck["state_dict"])
    return model.eval()


@torch.no_grad()
def probs(model, x, device, bs=32):
    out = {h: [] for h in HEAD_NAMES}
    for i in range(0, len(x), bs):
        o = model(x[i:i + bs].to(device))
        for h in HEAD_NAMES:
            out[h].append(softmax(o[h].float().cpu().numpy()))
    return {h: np.concatenate(v) for h, v in out.items()}


def group_boot_mean(values: np.ndarray, groups: np.ndarray, n_boot: int, seed: int):
    rng = np.random.default_rng(seed)
    ug, inv = np.unique(groups, return_inverse=True)
    members = [np.where(inv == g)[0] for g in range(len(ug))]
    stats = []
    for _ in range(n_boot):
        idx = np.concatenate([members[g] for g in rng.integers(0, len(ug), len(ug))])
        stats.append(values[idx].mean())
    return {"value": float(values.mean()), "ci95": [float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/phase2_convnext_tiny.yaml")
    args = ap.parse_args()
    cfg = load_config(ROOT / args.config)
    seed = cfg["seed"]
    set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    size = cfg["input_size"]
    n_boot = cfg["eval"]["n_boot"]
    out_dir = ROOT / "results" / "phase3" / cfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)

    proc = ROOT / cfg["processed_dir"]
    df = pd.read_parquet(proc / "surgwound.parquet")
    lab = encode_labels(df)
    names = df.image_name.to_numpy()
    splits = pd.read_csv(ROOT / "results" / "phase2" / "splits.csv")
    assert (splits.image_name == names).all()
    fold, G = splits.cv_fold.to_numpy(), splits.group.to_numpy()

    boxes = overlay_boxes(proc / "ocr.json", proc / "orange_boxes.json")
    has_overlay = np.array([len(boxes[n]) > 0 for n in names])
    fig_set = choose_figure_set(df, lab, has_overlay, seed)

    tf = build_transforms(cfg, train=False)
    imgs_model = load_images(cfg, ROOT, names)                       # what this model was trained on
    imgs_orig = load_images({**cfg, "image_variant": "original"}, ROOT, names)
    imgs_clean = load_images({**cfg, "image_variant": "inpainted"}, ROOT, names)
    to_x = lambda u8: torch.stack([tf(t) for t in u8])  # noqa: E731
    disp = v2.Resize(size, antialias=True)

    cam_rows, occ_rows, fig_cams = [], [], {}
    for k in range(cfg["cv"]["n_splits"]):
        model = load_fold_model(cfg, k, device)
        ev = np.where(fold == k)[0]
        ov = ev[has_overlay[ev]]
        figs = [i for i in ev if names[i] in fig_set]
        need = np.unique(np.r_[ov, figs]).astype(int)
        if len(need) == 0:
            continue
        x = to_x(imgs_model[need]).to(device)
        cams = {h: gradcam_maps(model, x, h, CRITICAL_CLASS[h], batch_size=8) for h in HEAD_NAMES}
        p_model = probs(model, x, device)
        for j, i in enumerate(need):
            n = names[i]
            if n in fig_set:
                fig_cams[n] = {"cams": {h: cams[h][j] for h in HEAD_NAMES},
                               "p": {h: float(p_model[h][j, CRITICAL_CLASS[h]]) for h in HEAD_NAMES},
                               "disp": disp(imgs_model[i]).permute(1, 2, 0).numpy()}
            if not has_overlay[i]:
                continue
            w, h_ = int(df.width[i]), int(df.height[i])
            region = box_mask(to_letterbox(boxes[n], w, h_, size), size)
            content = content_mask(w, h_, size)
            area = float((region & content).sum() / content.sum())
            for h in HEAD_NAMES:
                cam_rows.append({"image_name": n, "group": G[i], "head": h, "fold": k,
                                 "source_900plus": int(lab.source_900plus[i]),
                                 "cam_mass_on_overlay": mass_fraction(cams[h][j], region, content),
                                 "overlay_area_frac": area})
        # causal check: same fold model, original vs inpainted input, overlay images only
        if len(ov):
            po = probs(model, to_x(imgs_orig[ov]).to(device), device)
            pc = probs(model, to_x(imgs_clean[ov]).to(device), device)
            for j, i in enumerate(ov):
                for h in HEAD_NAMES:
                    c = CRITICAL_CLASS[h]
                    occ_rows.append({"image_name": names[i], "group": G[i], "head": h, "fold": k,
                                     "source_900plus": int(lab.source_900plus[i]),
                                     "p_crit_original": float(po[h][j, c]), "p_crit_inpainted": float(pc[h][j, c]),
                                     "argmax_original": int(po[h][j].argmax()), "argmax_inpainted": int(pc[h][j].argmax())})
        del model
        torch.cuda.empty_cache()

    cam_df = pd.DataFrame(cam_rows)
    occ_df = pd.DataFrame(occ_rows)
    cam_df.to_parquet(out_dir / "cam_overlay.parquet", index=False)
    occ_df.to_parquet(out_dir / "occlusion.parquet", index=False)

    summary = {"n_overlay_images": int(has_overlay.sum()), "cam": {}, "occlusion": {}}
    subsets = {"all_overlay_images": lambda d: np.ones(len(d), bool),
               "id_900plus": lambda d: (d.source_900plus == 1).to_numpy(),
               "other_sources": lambda d: (d.source_900plus == 0).to_numpy()}
    for h in HEAD_NAMES:
        ch = cam_df[cam_df["head"] == h]
        oh = occ_df[occ_df["head"] == h]
        for sub, sel in subsets.items():
            d, o = ch[sel(ch)], oh[sel(oh)]
            g = d.group.to_numpy()
            excess = (d.cam_mass_on_overlay - d.overlay_area_frac).to_numpy()
            summary["cam"].setdefault(h, {})[sub] = {
                "n": len(d),
                "mean_cam_mass_on_overlay": group_boot_mean(d.cam_mass_on_overlay.to_numpy(), g, n_boot, seed),
                "mean_overlay_area_frac": group_boot_mean(d.overlay_area_frac.to_numpy(), g, n_boot, seed),
                "mean_excess_mass": group_boot_mean(excess, g, n_boot, seed),
                "enrichment_ratio": float(d.cam_mass_on_overlay.mean() / d.overlay_area_frac.mean()),
                "frac_images_mass_gt_2x_area": float((d.cam_mass_on_overlay > 2 * d.overlay_area_frac).mean()),
            }
            if len(o):
                dp = (o.p_crit_inpainted - o.p_crit_original).to_numpy()
                summary["occlusion"].setdefault(h, {})[sub] = {
                    "n": len(o),
                    "mean_delta_p_critical": group_boot_mean(dp, o.group.to_numpy(), n_boot, seed),
                    "mean_abs_delta_p_critical": group_boot_mean(np.abs(dp), o.group.to_numpy(), n_boot, seed),
                    "decision_flips": int((o.argmax_original != o.argmax_inpainted).sum()),
                }
    save_json(summary, out_dir / "shortcut_summary.json")

    # figures: 6 images per page, original with overlay boxes, then one CAM per head
    order = [n for n in fig_set if n in fig_cams]
    cat = json.loads(FIGURE_SET_FILE.read_text())["category"]
    for page in range(0, len(order), 6):
        chunk = order[page:page + 6]
        fig, axes = plt.subplots(len(chunk), 1 + len(HEAD_NAMES), figsize=(3.2 * (1 + len(HEAD_NAMES)), 3.4 * len(chunk)))
        axes = np.atleast_2d(axes)
        for r, n in enumerate(chunk):
            i = int(np.where(names == n)[0][0])
            rgb = fig_cams[n]["disp"]
            axes[r, 0].imshow(rgb)
            for x0, y0, x1, y1 in to_letterbox(boxes[n], int(df.width[i]), int(df.height[i]), size):
                axes[r, 0].add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="lime", lw=1.2))
            truth = ", ".join(f"{h}={df[HEADS[h].get('source', h)][i] if pd.notna(df[HEADS[h].get('source', h)][i]) else 'uncertain'}"
                              for h in HEAD_NAMES)
            axes[r, 0].set_title(f"{n} ({cat[n]})\n{truth}", fontsize=7)
            for c, h in enumerate(HEAD_NAMES, start=1):
                axes[r, c].imshow(show_cam_on_image(rgb.astype(np.float32) / 255, fig_cams[n]["cams"][h], use_rgb=True))
                axes[r, c].set_title(f"{h}: P({HEADS[h]['classes'][CRITICAL_CLASS[h]]}) = {fig_cams[n]['p'][h]:.2f}", fontsize=8)
            for a in axes[r]:
                a.axis("off")
        fig.suptitle(f"Grad-CAM for the critical class of each head, {cfg['name']} (fold model that did not train on the image)", fontsize=9)
        fig.tight_layout()
        fig.savefig(out_dir / f"gradcam_{page // 6 + 1}.png", dpi=90)
        plt.close(fig)
    print(json.dumps(summary, indent=1)[:4000])


if __name__ == "__main__":
    main()
