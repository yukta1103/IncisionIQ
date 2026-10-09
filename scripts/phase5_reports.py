"""Phase 5: grounded template reports and the faithfulness checker.

1. Validates the claim extractor against the SurgWound expert reports and labels.
2. Builds the attribute JSON for every image from model A's out-of-fold
   predictions (tuned decision rule, Phase 4 abstention cut-offs and infection
   bands, all per fold from inner-val).
3. Renders a template report per image, extracts its claims, and scores them
   against the attribute JSON (faithfulness) and against the expert labels
   (correctness), with group-bootstrap CIs.

The VLM baseline is added later with the same checker (scripts/phase5_vlm.py).

Usage: python scripts/phase5_reports.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import HEAD_NAMES, HEADS, encode_labels, label_matrix  # noqa: E402
from src.eval.calibration import group_bootstrap  # noqa: E402
from src.eval.predictions import build_predictions  # noqa: E402
from src.report.claims import extract_claims  # noqa: E402
from src.report.faithfulness import expert_reference, score_claims, summarize  # noqa: E402
from src.report.template import render, source_reference  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402

OUT = ROOT / "results" / "phase5"
EXPERT_ATTRS = ["erythema", "edema", "exudate", "infection", "healing"]


def fmt(m, d=2):
    return f"{m['value']:.{d}f} [{m['ci95'][0]:.{d}f}, {m['ci95'][1]:.{d}f}]"


def validate_extractor(df) -> tuple[pd.DataFrame, list[str]]:
    rows = []
    for _, r in df.iterrows():
        ref = expert_reference(r)
        got = {}
        for c in extract_claims(r.report):
            got.setdefault(c.attribute, set()).add(c.value)
        for a in EXPERT_ATTRS:
            rows.append({"image_name": r.image_name, "split": r.split, "attribute": a, "label": ref[a],
                         "claim_made": a in got, "correct": ref[a] in got.get(a, set()) if ref[a] else None,
                         "wrong_value": bool(got.get(a, set()) - {ref[a]}) if ref[a] else None})
    R = pd.DataFrame(rows)
    L = R[R.label.notna()]
    tab = L.groupby(["attribute", "split"]).agg(n=("correct", "size"), claim_made=("claim_made", "mean"),
                                                agrees_with_label=("correct", "mean"),
                                                conflicting_value=("wrong_value", "mean")).round(3)
    U = R[R.label.isna()].groupby("attribute").agg(n_uncertain_label=("claim_made", "size"),
                                                   report_states_value=("claim_made", "mean")).round(3)
    md = ["## 1. Claim extractor validated on the SurgWound expert reports\n",
          "Agreement of claims extracted from each expert report with that image's expert label. "
          "The rules were tuned while inspecting failures on all splits, so this is a sanity check of the extractor, "
          "not a held-out estimate; free-text phrasing is covered by unit tests (`tests/test_claims.py`).\n",
          tab.reset_index().to_markdown(index=False),
          "\nExpert reports also state a value for attributes whose label is Uncertain (the question row is missing). "
          "Those claims are scored as unverifiable:\n", U.reset_index().to_markdown(index=False)]
    return tab, md


def attribute_json(cfg, df, lab, Y, G, names, fold):
    res = ROOT / cfg["results_dir"]
    inner = json.loads((res / "inner_splits.json").read_text(encoding="utf-8"))
    lg = pd.read_parquet(res / cfg["name"] / "logits.parquet")
    preds = build_predictions(cfg, lab, Y, G, names, inner, lg, None, cfg["seed"], with_baseline=False)[0]["finetuned"]["cv"]
    p4 = json.loads((ROOT / "results" / "phase4" / "metrics.json").read_text(encoding="utf-8"))
    op = json.loads((ROOT / "results" / "phase4" / "operating_point.json").read_text(encoding="utf-8"))
    band_rate = {b: op["bands"][b]["all"]["observed_rate"]["value"] for b in op["bands"]}
    out = []
    for i, n in enumerate(names):
        k = int(fold[i])
        a = {}
        for h in ("erythema", "edema", "exudate"):
            tau = p4["abstention"][h]["0.8"]["tau_per_fold"][str(k)]
            p = preds["P"][h][i]
            a[h] = {"value": HEADS[h]["classes"][int(preds["pred_tuned"][h][i])] if h == "exudate" else
                    ("present" if preds["pred_tuned"][h][i] == 1 else "absent"),
                    "uncertain": bool(p.max() < tau), "confidence": float(p.max())}
        pe = float(preds["P"]["infection"][i][1])
        t_flag, t_rev = op["per_fold"]["t_flag"][str(k)], op["per_fold"]["t_review"][str(k)]
        band = "high concern" if pe >= t_flag else ("uncertain" if pe >= t_rev else "low concern")
        a["infection"] = {"band": band, "observed_rate": band_rate[band]}
        out.append(a)
    return out


def score_reports(texts, sources, df, mode_rows=True):
    """Claim-level rows for each report vs its source JSON and vs the expert labels."""
    rows = []
    for i, (t, src) in enumerate(zip(texts, sources)):
        claims = extract_claims(t)
        exp = expert_reference(df.iloc[i])
        if src is not None:
            for r in score_claims(claims, source_reference(src), mode="source", ignore=("infection_level",)):
                rows.append({"i": i, "against": "source", **r})
        for r in score_claims(claims, exp, mode="expert"):
            rows.append({"i": i, "against": "expert", **r})
    return pd.DataFrame(rows)


def boot_summary(S: pd.DataFrame, against, img_idx, G, n_boot, seed):
    s = S[(S.against == against) & S.i.isin(img_idx)]
    by_img = {i: g for i, g in s.groupby("i")}
    idx = np.array(img_idx)

    def stat(ix):
        sub = [by_img[i] for i in idx[ix] if i in by_img]
        if not sub:
            return {"faithfulness": np.nan, "contradiction_rate": np.nan, "claims_per_report": 0.0}
        d = summarize(pd.concat(sub))
        return {"faithfulness": d["faithfulness"], "contradiction_rate": d["contradiction_rate"],
                "claims_per_report": d["n_claims"] / len(ix)}
    b = group_bootstrap(stat, len(idx), G[idx], n_boot, seed)
    return b, summarize(s)


def main():
    cfg = load_config(ROOT / "configs" / "phase3_convnext_tiny_inpainted.yaml")
    seed, n_boot = cfg["seed"], cfg["eval"]["n_boot"]
    set_seed(seed)
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(ROOT / cfg["processed_dir"] / "surgwound.parquet")
    lab = encode_labels(df)
    Y = label_matrix(lab)
    names = df.image_name.to_numpy()
    splits = pd.read_csv(ROOT / cfg["results_dir"] / "splits.csv")
    G, fold = splits.group.to_numpy(), splits.cv_fold.to_numpy()

    tab, md = validate_extractor(df)
    tab.to_csv(OUT / "extractor_validation.csv")

    attrs = attribute_json(cfg, df, lab, Y, G, names, fold)
    texts = [render(a) for a in attrs]
    pd.DataFrame({"image_name": names, "official_split": df.split, "attributes": [json.dumps(a) for a in attrs],
                  "template_report": texts}).to_parquet(OUT / "template_reports.parquet", index=False)

    # sanity: the expert reports scored by the same checker
    S_exp = score_reports(df.report.tolist(), [None] * len(df), df)
    S_tpl = score_reports(texts, attrs, df)
    S_tpl.to_parquet(OUT / "template_claims.parquet", index=False)

    subsets = {"all": np.arange(len(df)), "excl_900plus": np.where(lab.source_900plus == 0)[0],
               "official_test": np.where(df.split == "test")[0]}
    summary = {"template": {}, "expert_reports": {}}
    md.append("\n## 2. Template reports: faithfulness and correctness\n")
    md.append("Faithfulness = share of checkable claims that match the attribute JSON the report was generated from. "
              "Correctness = share of claims on labeled attributes that match the expert label. "
              "Contradiction = claims that conflict with the reference.\n")
    md.append("| subset | n images | claims per report | faithfulness to source | correctness vs expert labels | contradicts expert labels |")
    md.append("|---|---|---|---|---|---|")
    for s, idx in subsets.items():
        bs, rs = boot_summary(S_tpl, "source", idx, G, n_boot, seed)
        be, re_ = boot_summary(S_tpl, "expert", idx, G, n_boot, seed)
        summary["template"][s] = {"n": len(idx), "vs_source": {**rs, "boot": bs}, "vs_expert": {**re_, "boot": be}}
        md.append(f"| {s} | {len(idx)} | {fmt(bs['claims_per_report'], 1)} | {fmt(bs['faithfulness'], 3)} | "
                  f"{fmt(be['faithfulness'])} | {fmt(be['contradiction_rate'])} |")
        bx, rx = boot_summary(S_exp, "expert", idx, G, n_boot, seed)
        summary["expert_reports"][s] = {**rx, "boot": bx}

    md.append("\nReference point: the SurgWound expert reports themselves, scored by the same checker against their own "
              "labels (this measures checker plus report-label agreement, an upper bound for any report):\n")
    md.append("| subset | claims per report | correctness vs expert labels |")
    md.append("|---|---|---|")
    for s in subsets:
        b = summary["expert_reports"][s]["boot"]
        md.append(f"| {s} | {fmt(b['claims_per_report'], 1)} | {fmt(b['faithfulness'])} |")

    md.append("\nTemplate correctness by attribute (all images; claims on labeled attributes):\n")
    e = S_tpl[(S_tpl.against == "expert") & S_tpl.status.isin(["supported", "contradicted"])]
    per = e.groupby("attribute").status.apply(lambda x: pd.Series({"claims": len(x), "correct": (x == "supported").mean()})).unstack()
    md.append(per.round(3).reset_index().to_markdown(index=False))
    unc = {h: float(np.mean([a[h]["uncertain"] for a in attrs])) for h in ("erythema", "edema", "exudate")}
    bands = pd.Series([a["infection"]["band"] for a in attrs]).value_counts().to_dict()
    md.append(f"\nShare of reports stating 'uncertain' instead of a finding: {', '.join(f'{k} {v:.2f}' for k, v in unc.items())}; "
              f"infection bands: {bands}.")
    summary["uncertain_share"] = unc
    summary["bands"] = bands

    md.append("\n## 3. Examples (official test split)\n")
    rng = np.random.default_rng(seed)
    for i in rng.choice(subsets["official_test"], size=4, replace=False):
        r = df.iloc[i]
        md.append(f"**{r.image_name}** (expert: erythema {r.erythema}, edema {r.edema}, exudate {r.exudate}, "
                  f"infection risk {r.infection_risk})\n\n> {texts[i]}\n")
    save_json(summary, OUT / "metrics.json")
    (OUT / "tables.md").write_text("# Phase 5 tables\n\n" + "\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
