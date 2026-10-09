"""Paired group-bootstrap test: original (Phase 2) vs mitigated (Phase 3) model.

Both models are scored on the same images in every bootstrap resample of
same-patient groups, so the interval is for the difference itself. Decisions
use each model's tuned rule (alpha learned on its own inner-val), exactly as in
phase2_eval.

Usage: python scripts/phase3_paired_test.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import CRITICAL_CLASS, HEAD_NAMES, HEADS, encode_labels, label_matrix  # noqa: E402
from src.eval.metrics import scalar_metrics  # noqa: E402
from src.eval.predictions import build_predictions  # noqa: E402
from src.utils import ROOT, load_config, save_json  # noqa: E402

CONFIGS = {"original": "configs/phase2_convnext_tiny.yaml", "mitigated": "configs/phase3_convnext_tiny_inpainted.yaml"}
METRICS = ("macro_f1", "critical_auroc", "critical_recall", "critical_recall_subset")


def main():
    cfgs = {k: load_config(ROOT / v) for k, v in CONFIGS.items()}
    seed, n_boot = cfgs["original"]["seed"], cfgs["original"]["eval"]["n_boot"]
    df = pd.read_parquet(ROOT / cfgs["original"]["processed_dir"] / "surgwound.parquet")
    lab = encode_labels(df)
    Y = label_matrix(lab)
    names = df.image_name.to_numpy()
    splits = pd.read_csv(ROOT / "results" / "phase2" / "splits.csv")
    G = splits.group.to_numpy()

    preds = {}
    for k, cfg in cfgs.items():
        res = ROOT / cfg["results_dir"]
        inner = json.loads((res / "inner_splits.json").read_text(encoding="utf-8"))
        lg = pd.read_parquet(res / cfg["name"] / "logits.parquet")
        preds[k] = build_predictions(cfg, lab, Y, G, names, inner, lg, None, seed, with_baseline=False)[0]["finetuned"]["cv"]

    rng = np.random.default_rng(seed)
    out = {}
    for h in HEAD_NAMES:
        kh = HEAD_NAMES.index(h)
        for sub, smask in (("excl_900plus", lab.source_900plus.to_numpy() == 0), ("all", np.ones(len(df), bool))):
            m = smask & (Y[:, kh] >= 0)
            y, g = Y[m, kh], G[m]
            extra = lab.infection_high.to_numpy()[m] if h == "infection" else None
            args = {k: (preds[k]["P"][h][m], preds[k]["pred_tuned"][h][m]) for k in CONFIGS}
            ncls, crit = len(HEADS[h]["classes"]), CRITICAL_CLASS[h]
            point = {k: scalar_metrics(y, p, ncls, crit, extra, pr) for k, (p, pr) in args.items()}
            ug, inv = np.unique(g, return_inverse=True)
            members = [np.where(inv == i)[0] for i in range(len(ug))]
            diffs = {mt: [] for mt in METRICS}
            for _ in range(n_boot):
                idx = np.concatenate([members[i] for i in rng.integers(0, len(ug), len(ug))])
                e = extra[idx] if extra is not None else None
                r = {k: scalar_metrics(y[idx], p[idx], ncls, crit, e, pr[idx]) for k, (p, pr) in args.items()}
                for mt in METRICS:
                    if mt in r["original"]:
                        diffs[mt].append(r["mitigated"][mt] - r["original"][mt])
            out.setdefault(h, {})[sub] = {"n": int(m.sum())}
            for mt in METRICS:
                if mt not in point["original"]:
                    continue
                d = np.array(diffs[mt], float)
                d = d[~np.isnan(d)]
                out[h][sub][mt] = {
                    "original": float(point["original"][mt]), "mitigated": float(point["mitigated"][mt]),
                    "diff": float(point["mitigated"][mt] - point["original"][mt]),
                    "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
                    "frac_boot_mitigated_lower": float((d < 0).mean()),
                }
            if h == "infection":
                out[h][sub]["n_high"] = int(extra.sum())
    save_json(out, ROOT / "results" / "phase3" / "paired_test.json")
    for h in HEAD_NAMES:
        for sub, r in out[h].items():
            f = r["macro_f1"]
            print(f"{h:9s} {sub:13s} n={r['n']} macro F1 {f['original']:.3f} -> {f['mitigated']:.3f} "
                  f"diff {f['diff']:+.3f} [{f['ci95'][0]:+.3f}, {f['ci95'][1]:+.3f}]")


if __name__ == "__main__":
    main()
