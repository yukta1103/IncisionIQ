"""Phase 1: data audit. No modeling.

Usage: python scripts/phase1_audit.py [--config configs/phase1_audit.yaml] [--skip-ocr] [--skip-embed]

Every step caches its output under data/processed or results/phase1, so reruns
only recompute what is missing.
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
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data import dedup, ocr  # noqa: E402
from src.data.build import build  # noqa: E402
from src.data.schema import ATTRS, SPLITS, UNCERTAIN  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402

MISSING = "<missing>"


def step_build(cfg) -> pd.DataFrame:
    out = ROOT / cfg["processed_dir"]
    pq = out / "surgwound.parquet"
    if pq.exists():
        return pd.read_parquet(pq)
    raw = ROOT / cfg["raw_dir"]
    if not (raw / "test_report.json").exists():
        from huggingface_hub import hf_hub_download
        print("[build] downloading xuxuxuxuxu/SurgWound")
        for s in SPLITS:
            for kind in ("question", "report"):
                hf_hub_download("xuxuxuxuxu/SurgWound", f"{s}_{kind}.json", repo_type="dataset", local_dir=raw)
    print("[build] decoding images and pivoting")
    return build(ROOT / cfg["raw_dir"], out)


def step_split_check(df) -> dict:
    per_split = {s: set(df.loc[df.split == s, "image_name"]) for s in SPLITS}
    overlaps = {
        f"{a}&{b}": sorted(per_split[a] & per_split[b])
        for i, a in enumerate(SPLITS) for b in SPLITS[i + 1:]
    }
    multi = df.get("other_splits", pd.Series([""] * len(df)))
    sha_groups = df.groupby("sha256")["image_name"].apply(list)
    exact = [g for g in sha_groups if len(g) > 1]
    exact_cross = [g for g in exact if df.set_index("image_name").loc[g, "split"].nunique() > 1]
    return {
        "n_images": len(df),
        "images_per_split": {s: len(v) for s, v in per_split.items()},
        "image_name_overlap_between_splits": {k: len(v) for k, v in overlaps.items()},
        "image_names_with_rows_in_multiple_splits": int((multi != "").sum()),
        "byte_identical_groups": exact,
        "byte_identical_groups_crossing_splits": exact_cross,
        "split_is_image_level_by_name": all(len(v) == 0 for v in overlaps.values()) and (multi == "").all(),
    }


def step_class_counts(df, options, rare_thr) -> tuple[dict, pd.DataFrame]:
    tables, rows = {}, []
    for a in ATTRS:
        col = df[a].fillna(MISSING)
        t = pd.crosstab(col, df.split).reindex(columns=SPLITS, fill_value=0)
        order = [o for o in options[a] if o in t.index] + [o for o in t.index if o not in options[a]]
        t = t.loc[order]
        t["total"] = t.sum(axis=1)
        tables[a] = t
        for cls, r in t.iterrows():
            rows.append({
                "attribute": a, "class": cls, **{s: int(r[s]) for s in SPLITS}, "total": int(r["total"]),
                "rare": cls not in (MISSING, UNCERTAIN) and r["total"] < rare_thr,
                "absent_from_test": cls not in (MISSING,) and r["test"] == 0,
            })
        # options that never occur
        for o in options[a]:
            if o not in t.index:
                rows.append({"attribute": a, "class": o, **{s: 0 for s in SPLITS}, "total": 0,
                             "rare": True, "absent_from_test": True})
    return tables, pd.DataFrame(rows)


def step_missingness(df) -> dict:
    """What does a missing attribute row mean? Look at what the expert report says."""
    out = {}
    keywords = {
        "location": ["abdom", "patell", "knee", "ankle", "facial", "face", "hand", "manus", "cervical", "neck"],
        "closure": ["suture", "staple", "adhesive", "invisible", "closed with", "closure"],
        "exudate": ["exudate", "serous", "sanguineous", "purulent", "drainage"],
        "erythema": ["erythema", "redness"],
        "edema": ["edema", "swelling"],
    }
    for a, kws in keywords.items():
        miss = df[df[a].isna()]
        if miss.empty:
            continue
        rep = miss["report"].fillna("").str.lower()
        mentions = rep.apply(lambda s: [k for k in kws if k in s])
        out[a] = {
            "n_missing": len(miss),
            "frac_reports_mentioning_attribute_keyword": float((mentions.str.len() > 0).mean()),
            "examples": [
                {"image_name": n, "report": r}
                for n, r in miss[["image_name", "report"]].head(4).itertuples(index=False)
            ],
        }
    return out


def step_attr_crosstabs(df) -> dict:
    out = {}
    for a, b in [("infection_risk", "urgency"), ("healing", "infection_risk"),
                 ("exudate", "infection_risk"), ("erythema", "infection_risk")]:
        out[f"{a}_x_{b}"] = pd.crosstab(df[a].fillna(MISSING), df[b].fillna(MISSING)).to_dict()
    return out


# ---------------------------------------------------------------- dedup

def _thumb(path, size=220):
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((size, size))
        return np.asarray(im)


def contact_sheet(df, pairs, img_dir, out_path, title, per_page=12):
    pages = []
    for start in range(0, len(pairs), per_page):
        chunk = pairs[start:start + per_page]
        fig, axes = plt.subplots(len(chunk), 2, figsize=(6, 3 * len(chunk)))
        axes = np.atleast_2d(axes)
        for row, (i, j, score) in enumerate(chunk):
            for col, k in enumerate((i, j)):
                ax = axes[row, col]
                ax.imshow(_thumb(img_dir / df.image_name[k]))
                ax.set_title(f"{df.image_name[k]} [{df.split[k]}]" + (f"  {score}" if col == 0 else ""), fontsize=8)
                ax.axis("off")
        fig.suptitle(f"{title} (pairs {start + 1}-{start + len(chunk)})", fontsize=9)
        fig.tight_layout()
        p = out_path.with_name(f"{out_path.stem}_{start // per_page + 1:02d}.png")
        fig.savefig(p, dpi=90)
        plt.close(fig)
        pages.append(str(p.relative_to(ROOT)))
    return pages


def step_dedup(df, cfg, res_dir, skip_embed) -> dict:
    dc = cfg["dedup"]
    img_dir = ROOT / cfg["processed_dir"] / "images"
    paths = [img_dir / n for n in df.image_name]
    cache = ROOT / cfg["processed_dir"] / "phash_dist.npy"
    if cache.exists():
        D = np.load(cache)
    else:
        print("[dedup] pHash")
        D = dedup.phash_distance(paths)
        np.save(cache, D)

    split = df.split.to_numpy()
    iu = np.triu_indices(len(df), 1)
    dist = D[iu]
    cross = split[iu[0]] != split[iu[1]]
    sweep = {}
    for t in dc["phash_sweep"]:
        m = dist <= t
        pairs = list(zip(iu[0][m], iu[1][m]))
        cl = dedup.clusters_from_pairs(len(df), pairs)
        sweep[t] = {
            "pairs": int(m.sum()),
            "pairs_crossing_splits": int((m & cross).sum()),
            "clusters": len(cl),
            "images_in_clusters": sum(len(c) for c in cl),
            "clusters_crossing_splits": sum(len(set(split[c])) > 1 for c in cl),
        }
    nn = D.min(axis=1)

    review = [(int(i), int(j), f"d={int(D[i, j])}") for i, j in zip(*iu) if D[i, j] <= dc["phash_review_max"]]
    review.sort(key=lambda x: int(x[2][2:]))
    sheets = contact_sheet(df, review, img_dir, res_dir / "dedup" / "phash_pairs.png",
                           f"pHash pairs with Hamming <= {dc['phash_review_max']}") if review else []

    out = {
        "phash_sweep": sweep,
        "phash_nn_distance_quantiles": {q: float(np.quantile(nn, q)) for q in (0.01, 0.05, 0.25, 0.5)},
        "phash_review_pairs": [
            {"a": df.image_name[i], "b": df.image_name[j], "split_a": split[i], "split_b": split[j],
             "hamming": int(D[i, j])} for i, j, _ in review],
        "phash_contact_sheets": sheets,
    }

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.hist(nn, bins=range(0, 40), color="#4c72b0")
    ax.axvline(dc["phash_review_max"] + 0.5, color="k", ls="--", lw=1)
    ax.set_xlabel("pHash Hamming distance to nearest other image (mirror-aware)")
    ax.set_ylabel("images")
    fig.tight_layout()
    fig.savefig(res_dir / "dedup" / "phash_nn_hist.png", dpi=120)
    plt.close(fig)

    if not skip_embed:
        ecache = ROOT / cfg["processed_dir"] / "dino_emb.npy"
        if ecache.exists():
            E = np.load(ecache)
        else:
            import torch
            print("[dedup] DINOv2 embeddings")
            E = dedup.embed(paths, dc["embed_model"], "cuda" if torch.cuda.is_available() else "cpu")
            np.save(ecache, E)
        S = E @ E.T
        np.fill_diagonal(S, -1)
        sim = S[iu]
        m = sim >= dc["embed_review_min"]
        cand = sorted(((int(i), int(j), float(S[i, j])) for i, j in zip(iu[0][m], iu[1][m])),
                      key=lambda x: -x[2])
        # pairs that pHash did not already catch
        new = [(i, j, f"cos={s:.3f} d={int(D[i, j])}") for i, j, s in cand if D[i, j] > dc["phash_review_max"]]
        out["embed_review_pairs"] = [
            {"a": df.image_name[i], "b": df.image_name[j], "split_a": split[i], "split_b": split[j],
             "cosine": float(S[i, j]), "hamming": int(D[i, j])} for i, j, _ in new]
        out["embed_cosine_sweep"] = {
            t: {"pairs": int((sim >= t).sum()), "pairs_crossing_splits": int(((sim >= t) & cross).sum())}
            for t in (0.80, 0.85, 0.90, 0.95)}
        out["embed_contact_sheets"] = contact_sheet(
            df, new, img_dir, res_dir / "dedup" / "embed_pairs.png",
            f"DINOv2 cosine >= {dc['embed_review_min']} not caught by pHash") if new else []
    return out


# ---------------------------------------------------------------- same-patient groups

def _image_id(names):
    return names.str.extract(r"(\d+)")[0].astype(int).to_numpy()


def step_groups(df, cfg, res_dir) -> dict:
    """Leakage under several grouping rules. Rules only add edges, never remove
    verified ones, so each rule is a superset of 'verified'."""
    import yaml

    gc = cfg["groups"]
    review = yaml.safe_load(open(ROOT / gc["review_file"], encoding="utf-8"))
    idx = {n: i for i, n in enumerate(df.image_name)}

    def edges_from(groups):
        return [(idx[g[0]], idx[m]) for g in groups for m in g[1:]]

    verified = edges_from(review["exact_or_near_identical"] + review["same_patient_verified"])
    uncertain = edges_from(review["same_patient_uncertain"])

    E = np.load(ROOT / cfg["processed_dir"] / "dino_emb.npy")
    S = E @ E.T
    ids = _image_id(df.image_name)
    pos = {v: i for i, v in enumerate(ids)}
    adjacent = []
    for i, v in enumerate(ids):
        for k in range(1, gc["adjacent_id_gap"] + 1):
            j = pos.get(v + k)
            if j is not None and S[i, j] >= gc["adjacent_min_cos"]:
                adjacent.append((i, j))
    iu = np.triu_indices(len(df), 1)
    glob = [(int(i), int(j)) for i, j in zip(*iu) if S[i, j] >= gc["global_min_cos"]]

    # contact sheets of the ID-adjacent candidates, for re-review
    adj_pairs = sorted(((i, j, S[i, j]) for i, v in enumerate(ids) for k in (1, 2)
                        if (j := pos.get(v + k)) is not None and S[i, j] >= 0.70), key=lambda r: -r[2])
    contact_sheet(df, [(i, j, f"cos={c:.3f}") for i, j, c in adj_pairs],
                  ROOT / cfg["processed_dir"] / "images", res_dir / "dedup" / "adjacent_id_pairs.png",
                  "ID-adjacent pairs cos>=0.70")

    rules = {
        "verified": verified,
        "verified+uncertain": verified + uncertain,
        "conservative_auto": verified + uncertain + adjacent + glob,
    }
    split = df.split.to_numpy()
    out, group_cols = {}, {}
    for name, edges in rules.items():
        cl = dedup.clusters_from_pairs(len(df), edges)
        gid = np.arange(len(df))
        for k, c in enumerate(cl):
            gid[c] = len(df) + k
        group_cols[f"group_{name.replace('+', '_')}"] = gid
        test_leak = set()
        val_leak = set()
        for c in cl:
            sp = set(split[c])
            if "test" in sp and sp & {"train", "val"}:
                test_leak |= {df.image_name[i] for i in c if split[i] == "test"}
            if "val" in sp and "train" in sp:
                val_leak |= {df.image_name[i] for i in c if split[i] == "val"}
        out[name] = {
            "n_edges": len(edges),
            "groups": len(cl),
            "images_in_groups": sum(len(c) for c in cl),
            "largest_group": max((len(c) for c in cl), default=1),
            "groups_crossing_splits": sum(len(set(split[c])) > 1 for c in cl),
            "test_images_with_partner_in_train_or_val": len(test_leak),
            "val_images_with_partner_in_train": len(val_leak),
            "test_leak_images": sorted(test_leak, key=lambda n: int(n.split(".")[0])),
        }
    pd.DataFrame({"image_name": df.image_name, **group_cols}).to_parquet(
        ROOT / cfg["processed_dir"] / "groups.parquet", index=False)
    return out


# ---------------------------------------------------------------- sizes and OCR

def step_sizes(df, res_dir) -> dict:
    mp = df.width * df.height / 1e6
    short = np.minimum(df.width, df.height)
    aspect = df.width / df.height
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.2))
    axes[0].scatter(df.width, df.height, s=6, alpha=0.5)
    axes[0].set_xlabel("width (px)")
    axes[0].set_ylabel("height (px)")
    axes[1].hist(short, bins=40)
    axes[1].set_xlabel("short side (px)")
    axes[2].hist(aspect, bins=40)
    axes[2].set_xlabel("aspect ratio (w/h)")
    fig.tight_layout()
    fig.savefig(res_dir / "image_sizes.png", dpi=120)
    plt.close(fig)
    return {
        "width_quantiles": df.width.quantile([0, .05, .25, .5, .75, .95, 1]).to_dict(),
        "height_quantiles": df.height.quantile([0, .05, .25, .5, .75, .95, 1]).to_dict(),
        "short_side_lt_224": int((short < 224).sum()),
        "short_side_lt_384": int((short < 384).sum()),
        "megapixels_median": float(mp.median()),
        "aspect_ratio_quantiles": aspect.quantile([.05, .5, .95]).to_dict(),
        "formats": df.format.value_counts().to_dict(),
        "modes": df["mode"].value_counts().to_dict(),
        "size_by_split_median_short_side": df.assign(s=short).groupby("split").s.median().to_dict(),
    }


def step_ocr(df, cfg, res_dir) -> dict:
    oc = cfg["ocr"]
    img_dir = ROOT / cfg["processed_dir"] / "images"
    paths = [img_dir / n for n in df.image_name]
    passes = []
    for langs in oc["lang_passes"]:
        cache = ROOT / cfg["processed_dir"] / f"ocr_{'_'.join(langs)}.json"
        if cache.exists():
            dets = json.loads(cache.read_text(encoding="utf-8"))
        else:
            import torch
            print("[ocr] easyocr", langs)
            dets = dict(zip(df.image_name, ocr.run_ocr(paths, langs, gpu=torch.cuda.is_available())))
            cache.write_text(json.dumps(dets, ensure_ascii=False), encoding="utf-8")
        passes.append([dets[n] for n in df.image_name])
    dets = dict(zip(df.image_name, ocr.merge_passes(passes)))
    orange = {n: ocr.orange_redaction_boxes(p) for n, p in zip(df.image_name, paths)}
    (ROOT / cfg["processed_dir"] / "ocr.json").write_text(json.dumps(dets, ensure_ascii=False), encoding="utf-8")
    (ROOT / cfg["processed_dir"] / "orange_boxes.json").write_text(json.dumps(orange), encoding="utf-8")

    def confident(ds):
        return [d for d in ds if d["conf"] >= oc["min_conf"] and len(d["text"].strip()) >= oc["min_chars"]]

    df = df.copy()
    df["ocr_n_boxes"] = [len(confident(dets[n])) for n in df.image_name]
    df["ocr_text_area"] = [ocr.text_area_fraction(confident(dets[n]), w, h, 0.0)
                           for n, w, h in zip(df.image_name, df.width, df.height)]
    df["ocr_has_text"] = df.ocr_n_boxes > 0
    df["orange_box"] = [len(orange[n]) > 0 for n in df.image_name]
    df["any_overlay_detected"] = df.ocr_has_text | df.orange_box

    # Spot-check sheets: random sample of flagged images with boxes drawn.
    rng = np.random.default_rng(cfg["seed"])
    flagged = df[df.ocr_has_text].image_name.to_numpy()
    sample = rng.choice(flagged, size=min(24, len(flagged)), replace=False) if len(flagged) else []
    fig, axes = plt.subplots(4, 6, figsize=(18, 12))
    for ax in axes.flat:
        ax.axis("off")
    for ax, n in zip(axes.flat, sample):
        with Image.open(img_dir / n) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
        ax.imshow(im)
        for d in confident(dets[n]):
            x0, y0, x1, y1 = d["bbox"]
            ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="lime", lw=1.5))
        txt = " | ".join(d["text"] for d in confident(dets[n]))[:40]
        ax.set_title(f"{n}: {txt}", fontsize=7)
    fig.tight_layout()
    fig.savefig(res_dir / "ocr_flagged_sample.png", dpi=80)
    plt.close(fig)

    df[["image_name", "split", "ocr_n_boxes", "ocr_text_area", "ocr_has_text", "orange_box",
        "any_overlay_detected"]].to_parquet(
        ROOT / cfg["processed_dir"] / "ocr_flags.parquet", index=False)

    by_label = {}
    for a in ("infection_risk", "urgency", "healing"):
        by_label[a] = df.groupby(df[a].fillna(MISSING)).any_overlay_detected.agg(
            ["mean", "size"]).round(3).to_dict("index")
    return {
        "images_with_orange_redaction_box": int(df.orange_box.sum()),
        "images_with_any_detected_overlay": int(df.any_overlay_detected.sum()),
        "frac_any_overlay_by_split": df.groupby("split").any_overlay_detected.mean().round(3).to_dict(),
        "images_with_text": int(df.ocr_has_text.sum()),
        "frac_images_with_text": float(df.ocr_has_text.mean()),
        "frac_with_text_by_split": df.groupby("split").ocr_has_text.mean().round(3).to_dict(),
        "text_area_quantiles_among_flagged": df.loc[df.ocr_has_text, "ocr_text_area"].quantile(
            [.25, .5, .75, .95]).round(4).to_dict(),
        "frac_any_overlay_by_label": by_label,
        "flagged_sample": [str(x) for x in sample],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/phase1_audit.yaml")
    ap.add_argument("--skip-ocr", action="store_true")
    ap.add_argument("--skip-embed", action="store_true")
    args = ap.parse_args()
    cfg = load_config(ROOT / args.config)
    set_seed(cfg["seed"])
    res_dir = ROOT / cfg["results_dir"]
    (res_dir / "dedup").mkdir(parents=True, exist_ok=True)

    df = step_build(cfg)
    options = json.loads((ROOT / cfg["processed_dir"] / "options.json").read_text())
    summary = {"split_check": step_split_check(df)}

    tables, counts = step_class_counts(df, options, cfg["rare_class_threshold"])
    counts.to_csv(res_dir / "class_counts.csv", index=False)
    with open(res_dir / "class_counts.md", "w", encoding="utf-8") as f:
        for a, t in tables.items():
            f.write(f"### {a}\n\n{t.to_markdown()}\n\n")
    summary["rare_classes"] = counts[counts.rare][["attribute", "class", "total", "test"]].to_dict("records")
    summary["missing_per_attribute"] = {a: int(df[a].isna().sum()) for a in ATTRS}
    summary["uncertain_per_attribute"] = {a: int((df[a] == UNCERTAIN).sum()) for a in ATTRS}
    summary["missingness"] = step_missingness(df)
    summary["crosstabs"] = step_attr_crosstabs(df)
    summary["sizes"] = step_sizes(df, res_dir)
    summary["dedup"] = step_dedup(df, cfg, res_dir, args.skip_embed)
    if not args.skip_embed:
        summary["groups"] = step_groups(df, cfg, res_dir)
    if not args.skip_ocr:
        summary["ocr"] = step_ocr(df, cfg, res_dir)
    save_json(summary, res_dir / "summary.json")
    print("wrote", res_dir / "summary.json")


if __name__ == "__main__":
    main()
