"""Phase 6: what the verdict levels mean on out-of-fold predictions.

There are no patient answers in SurgWound, so the verdict is evaluated with no
symptoms reported (pain 0, not worsening, no fever, no drainage): the image
rules alone. For each level: share of images, observed Elevated and High rate
(surgeon labels) with group-bootstrap CIs, and how many High-risk images it
holds. Symptom overrides can only raise a verdict, so these rates bound what
the image contributes.

Usage: python scripts/phase6_verdict_eval.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import encode_labels  # noqa: E402
from src.eval.calibration import group_bootstrap  # noqa: E402
from src.triage.verdict import ON_TRACK, REVIEW, WATCH, PatientAnswers, verdict  # noqa: E402
from src.utils import ROOT, save_json  # noqa: E402

OUT = ROOT / "results" / "phase6"


def main():
    df = pd.read_parquet(ROOT / "data" / "processed" / "surgwound.parquet")
    lab = encode_labels(df)
    G = pd.read_csv(ROOT / "results" / "phase3" / "splits.csv").group.to_numpy()
    tpl = pd.read_parquet(ROOT / "results" / "phase5" / "template_reports.parquet")
    dep = json.loads((OUT / "deployment.json").read_text())
    calm = PatientAnswers(pain=0, pain_worsening=False, fever=False, drainage=False)
    levels = []
    for a in tpl.attributes:
        attrs = json.loads(a)
        attrs["infection"]["observed_rate"] = dep["band_rates"][attrs["infection"]["band"]]["rate"]
        levels.append(verdict(attrs, calm)["level"])
    levels = np.array(levels)
    elev, high = lab.infection.to_numpy() == 1, lab.infection_high.to_numpy() == 1
    out, md = {}, ["# Phase 6: verdict levels on out-of-fold predictions (no symptoms reported)\n",
                   "| subset | verdict | n | share | Elevated rate | High-risk images |", "|---|---|---|---|---|---|"]
    for s, m in (("excl_900plus", lab.source_900plus.to_numpy() == 0), ("all", np.ones(len(df), bool))):
        out[s] = {}
        for lv in (ON_TRACK, WATCH, REVIEW):
            idx = np.where(m & (levels == lv))[0]
            b = group_bootstrap(lambda ix, e=elev[idx]: {"rate": float(e[ix].mean()) if len(ix) else np.nan},
                                len(idx), G[idx], 2000, 42)["rate"]
            out[s][lv] = {"n": len(idx), "share": len(idx) / int(m.sum()), "elevated_rate": b,
                          "n_high": int(high[idx].sum()), "n_elevated": int(elev[idx].sum())}
            md.append(f"| {s} | {lv} | {len(idx)} | {len(idx) / m.sum():.2f} | {b['value']:.2f} "
                      f"[{b['ci95'][0]:.2f}, {b['ci95'][1]:.2f}] | {int(high[idx].sum())} of {int((m & high).sum())} |")
    save_json(out, OUT / "verdict_eval.json")
    (OUT / "verdict_eval.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
