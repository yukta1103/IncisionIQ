"""Phase 6: collect the decision parameters the demo needs into one file, and
check that they reproduce the evaluated system.

results/phase6/deployment.json holds, for model A (inpainted inputs):
  folds         per CV fold: decision-rule alpha, inner-train class prior and
                abstention cut-off tau per head; infection t_review and t_flag
  deployed_fold the single model the demo uses for every photo: fold 0, by fixed
                rule (the first fold), not by performance, with the parameters
                the cross-validation tested for that fold
  band_rates    observed Elevated rate per infection band, excluding ID 900+
  examples      demo images, chosen by the fixed rule in `select_examples`

Check: feeding the stored out-of-fold logits through src/triage/decide.py with
each image's fold parameters must reproduce the Phase 5 template attributes.

Usage: python scripts/phase6_build_deployment.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import HEAD_NAMES, HEADS, encode_labels, label_matrix  # noqa: E402
from src.eval.metrics import softmax  # noqa: E402
from src.eval.thresholds import class_prior  # noqa: E402
from src.triage.decide import attributes_from_probs  # noqa: E402
from src.utils import ROOT, load_config, save_json  # noqa: E402

CFG = "configs/phase3_convnext_tiny_inpainted.yaml"
OUT = ROOT / "results" / "phase6"
DEPLOYED_FOLD = 0
OCR_MAX_SIDE = 1024  # demo OCR resolution cap (training used 1280); effect: results/phase7/ocr_cap_1024.json
# Demo examples, one per slot: (description, required surgeon rating or None for any, required band).
# Stratified by surgeon label so the demo shows a mix, including a false alarm; blind to performance
# beyond the slot definitions themselves.
SLOTS = [("surgeon Low, predicted low concern", ("Low",), "low concern"),
         ("surgeon Elevated, predicted high concern", ("Medium", "High"), "high concern"),
         ("any surgeon rating, predicted referral band", None, "uncertain"),
         ("surgeon Low, predicted high concern (a false alarm)", ("Low",), "high concern")]


def select_examples(d: pd.DataFrame, ocr: dict, orange: dict) -> list[tuple[str, str]]:
    """Fixed rule: for each slot, the lowest-ID image that is in the official test split, held out by
    the deployed fold, has no OCR detection at all and no orange box, and meets the slot's surgeon
    rating and out-of-fold band. The chosen images were then checked by eye for captions and faces
    (none found)."""
    d = d.assign(id=d.image_name.str.removesuffix(".jpg").astype(int)).sort_values("id")
    ok = d[(d.split == "test") & (d.cv_fold == DEPLOYED_FOLD)
           & d.image_name.map(lambda n: not ocr.get(n) and not orange.get(n))]
    out = []
    for desc, ratings, band in SLOTS:
        m = ok[(ok.band == band) & (ok.infection_risk.isin(ratings) if ratings else True)]
        out.append((m.image_name.iloc[0], desc))
    return out


def main():
    cfg = load_config(ROOT / CFG)
    df = pd.read_parquet(ROOT / cfg["processed_dir"] / "surgwound.parquet")
    lab = encode_labels(df)
    Y = label_matrix(lab)
    names = df.image_name.to_numpy()
    idx_of = {n: i for i, n in enumerate(names)}
    res = ROOT / cfg["results_dir"]
    inner = json.loads((res / "inner_splits.json").read_text(encoding="utf-8"))
    fold = pd.read_csv(res / "splits.csv").cv_fold.to_numpy()
    alphas = json.loads((res / cfg["name"] / "metrics.json").read_text())["alphas"]["finetuned"]
    p4 = json.loads((ROOT / "results" / "phase4" / "metrics.json").read_text())
    op = json.loads((ROOT / "results" / "phase4" / "operating_point.json").read_text())
    K = cfg["cv"]["n_splits"]

    folds = {}
    for k in range(K):
        tr = np.array([idx_of[n] for n in inner[f"cv{k}"]["train"]])
        heads = {}
        for h in ("erythema", "edema", "exudate"):
            kh = HEAD_NAMES.index(h)
            heads[h] = {"alpha": alphas[f"cv{k}"][h]["alpha"],
                        "prior": class_prior(Y[tr, kh], len(HEADS[h]["classes"])).tolist(),
                        "tau": p4["abstention"][h]["0.8"]["tau_per_fold"][str(k)]}
        folds[k] = {"heads": heads, "t_review": op["per_fold"]["t_review"][str(k)], "t_flag": op["per_fold"]["t_flag"][str(k)]}
    band_rates = {b: {"rate": v["excl_900plus"]["observed_rate"]["value"], "ci95": v["excl_900plus"]["observed_rate"]["ci95"],
                      "n": v["excl_900plus"]["n"]} for b, v in op["bands"].items()}

    # reproduce the evaluated attributes from stored out-of-fold logits
    lg = pd.read_parquet(res / cfg["name"] / "logits.parquet")
    ev = lg[(lg.protocol == "cv") & (lg.role == "eval")].set_index("image_name")
    tpl = pd.read_parquet(ROOT / "results" / "phase5" / "template_reports.parquet").set_index("image_name")
    mismatches = 0
    for n in names:
        probs = {h: softmax(ev.loc[[n], [c for c in ev.columns if c.startswith(f"{h}_logit")]].to_numpy())[0] for h in HEAD_NAMES}
        a = attributes_from_probs(probs, folds[int(fold[idx_of[n]])], band_rates)
        ref = json.loads(tpl.loc[n, "attributes"])
        same = all(a[h]["value"] == ref[h]["value"] and a[h]["uncertain"] == ref[h]["uncertain"]
                   for h in ("erythema", "edema", "exudate")) and a["infection"]["band"] == ref["infection"]["band"]
        mismatches += not same
    print(f"reproduction check: {len(names) - mismatches}/{len(names)} images identical to the Phase 5 template attributes")
    assert mismatches == 0

    band = {n: json.loads(tpl.loc[n, "attributes"])["infection"]["band"] for n in names}
    proc = ROOT / cfg["processed_dir"]
    chosen = select_examples(pd.DataFrame({"image_name": names, "split": df.split.to_numpy(), "cv_fold": fold,
                                           "infection_risk": df.infection_risk.to_numpy(),
                                           "band": [band[n] for n in names]}),
                             json.loads((proc / "ocr.json").read_text(encoding="utf-8")),
                             json.loads((proc / "orange_boxes.json").read_text(encoding="utf-8")))
    examples = [{"image_name": n, "cv_fold": int(fold[idx_of[n]]), "official_split": df.split[idx_of[n]],
                 "infection_risk": df.infection_risk[idx_of[n]], "band_out_of_fold": band[n], "slot": slot}
                for n, slot in chosen]
    assert all(e["cv_fold"] == DEPLOYED_FOLD for e in examples)
    save_json({"model": cfg["name"], "config": CFG, "deployed_fold": DEPLOYED_FOLD, "ocr_max_side": OCR_MAX_SIDE,
               "folds": folds,
               "band_rates": band_rates, "band_rates_subset": "excluding ID 900+ (grouped CV, out-of-fold, all folds pooled)",
               "examples": examples,
               "notes": "Every photo is scored by the fold 0 model with the parameters the cross-validation tested for "
                        "fold 0. The examples are fold 0 held-out images, so their results are out-of-fold."},
              OUT / "deployment.json")
    print(json.dumps(examples, indent=1))


if __name__ == "__main__":
    main()
