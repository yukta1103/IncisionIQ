"""Phase 2 training.

Runs the primary protocol (grouped 5-fold CV over all images) and the secondary
protocol (official test minus leaked images). Saves per-image logits for the
outer folds (out-of-fold), inner-val logits (for Phase 4 calibration), penultimate
features, and checkpoints.

Usage: python scripts/phase2_train.py [--config ...] [--folds 0,1] [--skip-secondary] [--epochs N]
"""
import argparse
import copy
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.dataset import load_cache  # noqa: E402
from src.data.labels import HEAD_NAMES, encode_labels, label_matrix  # noqa: E402
from src.data.splits import inner_split, outer_folds, secondary_split  # noqa: E402
from src.train.loop import predict, train_model  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402


def logits_frame(names, logits, protocol, fold, role):
    d = {"image_name": names, "protocol": protocol, "fold": fold, "role": role}
    for h in HEAD_NAMES:
        for c in range(logits[h].shape[1]):
            d[f"{h}_logit{c}"] = logits[h][:, c]
    return pd.DataFrame(d)


inner_splits: dict = {}


def run_one(tag, protocol, fold, tr_idx, va_idx, ev_idx, images, Y, names, cfg, device, seed, out_dir, ckpt_dir):
    print(f"[{tag}] train {len(tr_idx)}  inner-val {len(va_idx)}  eval {len(ev_idx)}", flush=True)
    t0 = time.time()
    model, best, hist, cand_summary = None, {"loss": float("inf")}, None, []
    for ci, over in enumerate(cfg["train"].get("candidates") or [{}]):
        ccfg = copy.deepcopy(cfg)
        ccfg["train"].update(over)
        print(f"[{tag}] candidate {ci} {over}", flush=True)
        m, b, h = train_model(images, Y, tr_idx, va_idx, ccfg, device, seed, log=lambda s: print(s, flush=True))
        cand_summary.append({"candidate": ci, **over, "best_epoch": b["epoch"], "inner_val_loss": b["loss"]})
        pd.DataFrame(h).assign(candidate=ci).to_csv(out_dir / f"history_{tag}_c{ci}.csv", index=False)
        if b["loss"] < best["loss"]:
            model, best, hist = m, {**b, "candidate": ci, "overrides": over}, h
        else:
            del m
        torch.cuda.empty_cache()
    ev_logits, ev_feat = predict(model, images, Y, ev_idx, cfg, device, return_features=True)
    va_logits = predict(model, images, Y, va_idx, cfg, device)
    best.pop("state", None)
    torch.save({"state_dict": model.state_dict(), "best_epoch": best["epoch"], "candidate": best["candidate"],
                "overrides": best["overrides"], "cfg": cfg,
                "train_idx": tr_idx, "val_idx": va_idx, "eval_idx": ev_idx}, ckpt_dir / f"{tag}.pt")
    np.save(out_dir / f"features_{tag}.npy", ev_feat)
    pd.DataFrame(cand_summary).to_csv(out_dir / f"candidates_{tag}.csv", index=False)
    print(f"[{tag}] selected candidate {best['candidate']} epoch {best['epoch']} val loss {best['loss']:.3f} "
          f"({(time.time() - t0) / 60:.1f} min)", flush=True)
    inner_splits[tag] = {"train": list(names[tr_idx]), "val": list(names[va_idx]), "eval": list(names[ev_idx])}
    return [logits_frame(names[ev_idx], ev_logits, protocol, fold, "eval"),
            logits_frame(names[va_idx], va_logits, protocol, fold, "inner_val")], best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/phase2_convnext_tiny.yaml")
    ap.add_argument("--folds", default=None, help="comma-separated subset of outer folds")
    ap.add_argument("--skip-secondary", action="store_true")
    ap.add_argument("--epochs", type=int, default=None, help="override, for smoke tests only")
    ap.add_argument("--tag-suffix", default="")
    ap.add_argument("--set", nargs="*", default=[], help="config overrides, e.g. train.lr_backbone=2e-5")
    args = ap.parse_args()
    cfg = load_config(ROOT / args.config)
    for kv in args.set:
        key, val = kv.split("=", 1)
        *path, last = key.split(".")
        d = cfg
        for p_ in path:
            d = d[p_]
        d[last] = yaml.safe_load(val)
    if args.epochs:
        cfg["train"]["epochs"] = args.epochs
    seed = cfg["seed"]
    set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    proc = ROOT / cfg["processed_dir"]
    out_dir = ROOT / cfg["results_dir"] / (cfg["name"] + args.tag_suffix)
    ckpt_dir = ROOT / cfg["checkpoint_dir"] / (cfg["name"] + args.tag_suffix)
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(proc / "surgwound.parquet")
    groups = pd.read_parquet(proc / "groups.parquet")
    assert (groups.image_name == df.image_name).all()
    G = groups[cfg["group_column"]].to_numpy()
    lab = encode_labels(df)
    Y = label_matrix(lab)
    names = df.image_name.to_numpy()
    images = load_cache(proc / "images", names, cfg["cache_size"], proc / f"cache_{cfg['cache_size']}.pt")

    fold = outer_folds(lab, G, cfg["cv"]["n_splits"], seed)
    sec = secondary_split(df, G, ROOT / cfg["review_file"])
    split_info = pd.DataFrame({"image_name": names, "group": G, "cv_fold": fold, "official_split": df.split})
    split_info["secondary_role"] = "unused"
    split_info.loc[sec["train_idx"], "secondary_role"] = "train"
    split_info.loc[sec["test_idx"], "secondary_role"] = "test"
    split_info.to_csv(ROOT / cfg["results_dir"] / "splits.csv", index=False)
    save_json({k: v for k, v in sec.items() if k in ("removed_test", "excluded_train")} |
              {"n_train": len(sec["train_idx"]), "n_test": len(sec["test_idx"])},
              ROOT / cfg["results_dir"] / "secondary_split.json")

    frames, bests = [], {}
    folds = range(cfg["cv"]["n_splits"]) if args.folds is None else [int(f) for f in args.folds.split(",")]
    for k in folds:
        outer_tr = np.where(fold != k)[0]
        ev = np.where(fold == k)[0]
        tr, va = inner_split(outer_tr, lab, G, cfg["cv"]["n_inner"], seed + k)
        assert not set(G[tr]) & set(G[ev]) and not set(G[va]) & set(G[ev]) and not set(G[tr]) & set(G[va])
        f, b = run_one(f"cv{k}", "cv", k, tr, va, ev, images, Y, names, cfg, device, seed + k, out_dir, ckpt_dir)
        frames += f
        bests[f"cv{k}"] = {"candidate": b["candidate"], "epoch": b["epoch"], "inner_val_loss": b["loss"]}

    if not args.skip_secondary:
        tr, va = inner_split(sec["train_idx"], lab, G, cfg["cv"]["n_inner"], seed + 100)
        assert not set(G[np.r_[tr, va]]) & set(G[sec["test_idx"]])
        f, b = run_one("secondary", "secondary", -1, tr, va, sec["test_idx"], images, Y, names, cfg,
                       device, seed + 100, out_dir, ckpt_dir)
        frames += f
        bests["secondary"] = {"candidate": b["candidate"], "epoch": b["epoch"], "inner_val_loss": b["loss"]}

    pd.concat(frames).to_parquet(out_dir / "logits.parquet", index=False)
    if args.folds is None and not args.skip_secondary:
        save_json(inner_splits, ROOT / cfg["results_dir"] / "inner_splits.json")
    save_json({"best_epochs": bests, "config": cfg}, out_dir / "train_summary.json")
    print("done", out_dir)


if __name__ == "__main__":
    main()
