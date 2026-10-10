"""Phase 5: VLM baseline vs grounded template reports, scored by the claim checker.

Report sets (all scored against the SurgWound expert labels):
  template   our template, rendered from model A's out-of-fold predictions
  vlm_A      Claude Opus 5.5 free-text report (SurgWound report instruction)
  vlm_B      Claude Opus 5.5 structured attributes, rendered with our template

Primary: grouped-CV images excluding ID 900+ (n = 613); also all images and the
official test split. Run-to-run variation: three runs on the official test split.

Usage: python scripts/phase5_compare.py [--simulate]
  --simulate  replace VLM outputs with expert reports (A) and expert labels (B)
              to test the scoring pipeline end to end without API calls
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import CRITICAL_CLASS, HEADS, encode_labels, label_matrix, HEAD_NAMES  # noqa: E402
from src.eval.metrics import cluster_bootstrap, paired_diff_ci  # noqa: E402
from src.report.claims import extract_claims  # noqa: E402
from src.report.evaluate import boot_rates, paired_rate_diff, score_reports  # noqa: E402
from src.report.faithfulness import expert_reference  # noqa: E402
from src.report.template import render  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402

OUT = ROOT / "results" / "phase5"
SETS = ("template", "vlm_A", "vlm_B")
RATES = ("correctness", "hallucination_rate", "reports_with_contradiction", "unverifiable_share", "claims_per_report")
VLM_TO_OURS = {"erythema": {"none": "absent", "present": "present"}, "edema": {"none": "absent", "present": "present"}}


def fmt(m, d=2):
    v, (lo, hi) = m["value"], m["ci95"]
    return "n/a" if v != v else f"{v:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]"


def fmt_diff(m):
    return f"{m['value']:+.2f} [{m['ci95'][0]:+.2f}, {m['ci95'][1]:+.2f}]"


def b_attrs(js: dict) -> dict:
    return {"erythema": {"value": VLM_TO_OURS["erythema"][js["erythema"]], "uncertain": False},
            "edema": {"value": VLM_TO_OURS["edema"][js["edema"]], "uncertain": False},
            "exudate": {"value": js["exudate"], "uncertain": False},
            "infection": {"value": js["infection_risk"]}}


def simulated_outputs(df) -> pd.DataFrame:
    inv = {"Existent": "present", "Non-existent": "none"}
    ex = {"Non-existent": "none", "Serous": "non_purulent", "Sanguineous": "non_purulent", "Purulent": "purulent",
          "Seropurulent": "purulent"}
    rows = []
    for run in ("run1", "run2", "run3"):
        sub = df if run == "run1" else df[df.split == "test"]
        for r in sub.itertuples():
            rows.append({"image_name": r.image_name, "run": run, "condition": "A", "result_type": "succeeded",
                         "stop_reason": "end_turn", "text": r.report})
            js = {"erythema": inv.get(r.erythema, "none"), "edema": inv.get(r.edema, "none"),
                  "exudate": ex.get(r.exudate, "none"), "infection_risk": "low" if r.infection_risk == "Low" else "elevated"}
            rows.append({"image_name": r.image_name, "run": run, "condition": "B", "result_type": "succeeded",
                         "stop_reason": "end_turn", "text": json.dumps(js)})
    return pd.DataFrame(rows)


def texts_for(vlm, df, run, cond):
    """Report text per df row (None if the request failed or was refused), plus parsed B JSON."""
    sub = vlm[(vlm.run == run) & (vlm.condition == cond)].set_index("image_name")
    texts, parsed = [], []
    for n in df.image_name:
        ok = n in sub.index and sub.loc[n, "result_type"] == "succeeded" and sub.loc[n, "stop_reason"] == "end_turn"
        if not ok:
            texts.append(None)
            parsed.append(None)
            continue
        t = sub.loc[n, "text"]
        if cond == "B":
            try:
                js = json.loads(t)
                parsed.append(js)
                texts.append(render(b_attrs(js)))
            except (json.JSONDecodeError, KeyError):
                texts.append(None)
                parsed.append(None)
        else:
            texts.append(t)
            parsed.append(None)
    return texts, parsed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulate", action="store_true")
    args = ap.parse_args()
    cfg = load_config(ROOT / "configs" / "phase3_convnext_tiny_inpainted.yaml")
    seed, n_boot = cfg["seed"], cfg["eval"]["n_boot"]
    set_seed(seed)
    df = pd.read_parquet(ROOT / cfg["processed_dir"] / "surgwound.parquet")
    lab = encode_labels(df)
    Y = label_matrix(lab)
    G = pd.read_csv(ROOT / cfg["results_dir"] / "splits.csv").group.to_numpy()
    tpl = pd.read_parquet(OUT / "template_reports.parquet")
    assert (tpl.image_name == df.image_name).all()
    vlm = simulated_outputs(df) if args.simulate else pd.read_parquet(OUT / "vlm" / "vlm_outputs.parquet")
    out_dir = OUT / ("vlm_simulated" if args.simulate else "vlm")
    out_dir.mkdir(parents=True, exist_ok=True)

    subsets = {"excl_900plus": np.where(lab.source_900plus == 0)[0], "all": np.arange(len(df)),
               "official_test": np.where(df.split == "test")[0]}
    texts = {"template": tpl.template_report.tolist()}
    texts["vlm_A"], _ = texts_for(vlm, df, "run1", "A")
    texts["vlm_B"], parsed_B = texts_for(vlm, df, "run1", "B")
    S = {k: score_reports(v, [None] * len(df), df) for k, v in texts.items()}
    metrics = {"n_failed_or_refused": {k: int(sum(t is None for t in v)) for k, v in texts.items()},
               "stop_reasons": vlm.groupby(["run", "condition"]).stop_reason.value_counts(dropna=False)
               .rename("n").reset_index().to_dict("records")}
    if "input_tokens" in vlm and vlm.input_tokens.notna().any():
        metrics["tokens"] = {"input": int(vlm.input_tokens.sum()), "output": int(vlm.output_tokens.sum()),
                             "cost_usd_batch": float((vlm.input_tokens.sum() * 2 + vlm.output_tokens.sum() * 10) / 1e6)}

    md = ["# Phase 5: VLM baseline vs grounded template reports\n",
          "All three report sets are scored by the same claim checker against the SurgWound expert labels. "
          "Correctness = supported / (supported + contradicted). Hallucination rate = contradicted claims / all "
          "extracted claims. Unverifiable = claims on attributes whose expert label is Uncertain. "
          "Images whose VLM request failed or was refused are excluded from that set "
          f"(failed or refused: {metrics['n_failed_or_refused']}).\n"]
    md.append("## Claim-level comparison (run 1)\n")
    md.append("| subset | report set | n | claims per report | correctness | hallucination rate | reports with a contradiction | unverifiable share |")
    md.append("|---|---|---|---|---|---|---|---|")
    for s, idx in subsets.items():
        metrics.setdefault("rates", {})[s] = {}
        for k in SETS:
            ok = np.array([i for i in idx if texts[k][i] is not None])
            b = boot_rates(S[k], "expert", ok, G, n_boot, seed)
            metrics["rates"][s][k] = {"n": len(ok), **b}
            md.append(f"| {s} | {k} | {len(ok)} | {fmt(b['claims_per_report'], 1)} | {fmt(b['correctness'])} | "
                      f"{fmt(b['hallucination_rate'])} | {fmt(b['reports_with_contradiction'])} | {fmt(b['unverifiable_share'])} |")
    md.append("\nPaired differences vs template (same group resamples, images where both sets have a report):\n")
    md.append("| subset | comparison | correctness diff | hallucination rate diff |")
    md.append("|---|---|---|---|")
    for s, idx in subsets.items():
        for k in ("vlm_A", "vlm_B"):
            both = np.array([i for i in idx if texts[k][i] is not None])
            dc = paired_rate_diff(S[k], S["template"], both, G, n_boot, seed, "correctness")
            dh = paired_rate_diff(S[k], S["template"], both, G, n_boot, seed, "hallucination_rate")
            metrics.setdefault("paired_vs_template", {}).setdefault(s, {})[k] = {"correctness": dc, "hallucination_rate": dh}
            md.append(f"| {s} | {k} minus template | {fmt_diff(dc)} | {fmt_diff(dh)} |")

    md.append("\n### Correctness by attribute (excluding ID 900+)\n")
    md.append("| attribute | " + " | ".join(f"{k} claims | {k} correct" for k in SETS) + " |")
    md.append("|---|" + "---|---|" * len(SETS))
    per = {}
    for k in SETS:
        e = S[k][(S[k].against == "expert") & S[k].i.isin(subsets["excl_900plus"]) & S[k].status.isin(["supported", "contradicted"])]
        per[k] = e.groupby("attribute").status.agg(n="size", correct=lambda x: (x == "supported").mean())
    for a in ("erythema", "edema", "exudate", "infection", "infection_level", "healing"):
        cells = []
        for k in SETS:
            if a in per[k].index:
                cells += [str(int(per[k].loc[a, "n"])), f"{per[k].loc[a, 'correct']:.2f}"]
            else:
                cells += ["0", "n/a"]
        md.append(f"| {a} | " + " | ".join(cells) + " |")

    # ---- condition B as a classifier vs model A
    md.append("\n## Condition B as a zero-shot classifier vs model A (excluding ID 900+)\n")
    md.append("Model A uses its tuned decision rule; infection for model A is the flag decision (high-concern band). "
              "Macro F1 and critical-class recall from hard decisions, group-bootstrap CIs, paired difference on the same images.\n")
    md.append("| head | n | macro F1 VLM-B | macro F1 model A | diff (VLM-B minus A) | critical recall VLM-B | critical recall model A |")
    md.append("|---|---|---|---|---|---|---|")
    tpl_attrs = [json.loads(a) for a in tpl.attributes]
    vb_map = {"erythema": lambda js: 1 if js["erythema"] == "present" else 0,
              "edema": lambda js: 1 if js["edema"] == "present" else 0,
              "exudate": lambda js: ["none", "non_purulent", "purulent"].index(js["exudate"]),
              "infection": lambda js: 1 if js["infection_risk"] == "elevated" else 0}
    ma_map = {"erythema": lambda a: 1 if a["erythema"]["value"] == "present" else 0,
              "edema": lambda a: 1 if a["edema"]["value"] == "present" else 0,
              "exudate": lambda a: ["none", "non_purulent", "purulent"].index(a["exudate"]["value"]),
              "infection": lambda a: 1 if a["infection"]["band"] == "high concern" else 0}
    for k_h, h in enumerate(HEAD_NAMES):
        m = np.zeros(len(df), bool)
        m[subsets["excl_900plus"]] = True
        m &= (Y[:, k_h] >= 0) & np.array([p is not None for p in parsed_B])
        idx = np.where(m)[0]
        k = len(HEADS[h]["classes"])
        y = Y[idx, k_h]
        pv = np.array([vb_map[h](parsed_B[i]) for i in idx])
        pa = np.array([ma_map[h](tpl_attrs[i]) for i in idx])
        rv, sv = cluster_bootstrap(y, np.eye(k)[pv], G[idx], k, CRITICAL_CLASS[h], n_boot, seed, pred=pv)
        ra, sa = cluster_bootstrap(y, np.eye(k)[pa], G[idx], k, CRITICAL_CLASS[h], n_boot, seed, pred=pa)
        d = paired_diff_ci(sv, sa, "macro_f1")
        metrics.setdefault("classifier", {})[h] = {"n": len(idx), "vlm_B": rv, "model_A": ra, "diff_macro_f1": d}
        md.append(f"| {h} | {len(idx)} | {fmt(rv['macro_f1'])} | {fmt(ra['macro_f1'])} | {d['mean_diff']:+.2f} "
                  f"[{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}] | {fmt(rv['critical_recall'])} | {fmt(ra['critical_recall'])} |")

    # ---- run-to-run variation on the official test split
    md.append("\n## Run-to-run variation (official test split, 3 runs)\n")
    test = subsets["official_test"]
    md.append("| condition | run | n | correctness | hallucination rate |")
    md.append("|---|---|---|---|---|")
    per_run_claims = {}
    for cond in ("A", "B"):
        for run in ("run1", "run2", "run3"):
            t, p = texts_for(vlm, df, run, cond)
            Sr = score_reports(t, [None] * len(df), df)
            ok = np.array([i for i in test if t[i] is not None])
            b = boot_rates(Sr, "expert", ok, G, n_boot, seed)
            metrics.setdefault("runs", {}).setdefault(cond, {})[run] = {"n": len(ok), **b}
            md.append(f"| {cond} | {run} | {len(ok)} | {fmt(b['correctness'])} | {fmt(b['hallucination_rate'])} |")
            per_run_claims[(cond, run)] = {i: {(c.attribute, c.value) for c in extract_claims(t[i])} if t[i] else None
                                           for i in test}
            if cond == "B":
                per_run_claims[("Bjson", run)] = {i: p[i] for i in test}
    md.append("\nAgreement across the 3 runs (share of test images where all three runs give the same answer):\n")
    md.append("| condition | attribute | agreement |")
    md.append("|---|---|---|")
    for a in ("erythema", "edema", "exudate", "infection"):
        same = []
        for i in test:
            vals = [per_run_claims[("A", r)][i] for r in ("run1", "run2", "run3")]
            if any(v is None for v in vals):
                continue
            same.append(len({frozenset(x for x in v if x[0] == a) for v in vals}) == 1)
        metrics.setdefault("agreement", {}).setdefault("A", {})[a] = float(np.mean(same)) if same else np.nan
        md.append(f"| A (claims extracted from free text) | {a} | {np.mean(same):.2f} (n={len(same)}) |")
    for key in ("erythema", "edema", "exudate", "infection_risk"):
        same = []
        for i in test:
            vals = [per_run_claims[("Bjson", r)][i] for r in ("run1", "run2", "run3")]
            if any(v is None for v in vals):
                continue
            same.append(len({v[key] for v in vals}) == 1)
        metrics.setdefault("agreement", {}).setdefault("B", {})[key] = float(np.mean(same)) if same else np.nan
        md.append(f"| B (structured) | {key} | {np.mean(same):.2f} (n={len(same)}) |")

    # ---- concrete contradictions from condition A
    md.append("\n## Examples: condition A contradicting the expert labels\n")
    ex = S["vlm_A"][(S["vlm_A"].against == "expert") & (S["vlm_A"].status == "contradicted")]
    picked, seen_attr = [], {}
    for _, r in ex.sample(frac=1.0, random_state=seed).iterrows():
        if seen_attr.get(r.attribute, 0) >= 2 or r.i in [p[0] for p in picked]:
            continue
        picked.append((r.i, r.attribute, r.value, r.reference))
        seen_attr[r.attribute] = seen_attr.get(r.attribute, 0) + 1
        if len(picked) == 8:
            break
    examples = []
    for i, a, v, ref in picked:
        row = df.iloc[i]
        clause = next((c.text for c in extract_claims(texts["vlm_A"][i]) if c.attribute == a and c.value == v), "")
        exp = expert_reference(row)
        examples.append({"image_name": row.image_name, "attribute": a, "vlm_claim": v, "expert_label": ref,
                         "clause": clause, "source_900plus": int(lab.source_900plus[i])})
        md.append(f"- **{row.image_name}**{' (ID 900+)' if lab.source_900plus[i] else ''}: {a} claimed **{v}**, "
                  f"expert label **{ref}**. Model text: \"{clause.strip()[:220]}\". "
                  f"(Expert labels: erythema {exp['erythema']}, edema {exp['edema']}, exudate {exp['exudate']}, "
                  f"infection {exp['infection']}.)")
    metrics["examples"] = examples
    save_json(metrics, out_dir / "metrics.json")
    pd.DataFrame({"image_name": df.image_name, "vlm_A": texts["vlm_A"], "vlm_B_rendered": texts["vlm_B"]}).to_parquet(
        out_dir / "reports.parquet", index=False)
    (out_dir / "comparison.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
