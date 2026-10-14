"""Phase 5: VLM baseline vs grounded template reports, scored by the claim checker.

Report sets (all scored against the SurgWound expert labels):
  template   our template, rendered from model A's out-of-fold predictions
  vlm_A      Claude Opus 5.5 free-text report (SurgWound report instruction)
  vlm_B      Claude Opus 5.5 structured attributes, rendered with our template

Refusals and failed requests (no usable output) are scored two ways:
  primary    counted as incorrect: every expert-labeled attribute of that image
             counts as an incorrect claim in correctness; in the classifier view
             the image is a missed finding (for infection, a missed Elevated case)
  secondary  excluded
The rate of claims contradicting surgeon labels (contradicted claims / all extracted
claims) is computed on produced reports only; a refusal is not a contradiction.

Primary subset: images excluding ID 900+ (n = 613); also all images and the
official test split. Run-to-run variation: three runs on the official test split.

Usage: python scripts/phase5_compare.py [--simulate]
  --simulate  replace VLM outputs with expert reports (A) and expert labels (B),
              with a few injected refusals, to test the scoring pipeline end to
              end without API calls (written to results/phase5/vlm_simulated/)
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import CRITICAL_CLASS, HEAD_NAMES, HEADS, encode_labels, label_matrix  # noqa: E402
from src.eval.calibration import group_bootstrap  # noqa: E402
from src.eval.metrics import cluster_bootstrap, paired_diff_ci  # noqa: E402
from src.report.claims import extract_claims  # noqa: E402
from src.report.markdown_claims import extract_markdown_claims  # noqa: E402
from src.report.evaluate import claim_counts, rates, score_reports  # noqa: E402
from src.report.faithfulness import expert_reference  # noqa: E402
from src.report.template import render  # noqa: E402
from src.utils import ROOT, load_config, save_json, set_seed  # noqa: E402

OUT = ROOT / "results" / "phase5"
SETS = ("template", "vlm_A", "vlm_B")
MAIN_ATTRS = ("erythema", "edema", "exudate", "infection", "healing")
# attributes where the condition A checker agrees with hand labels at >= 0.96 (phase5_markdown_validation.py)
VALIDATED_ATTRS = ("erythema", "edema", "infection")
EXTRACTOR = {"template": extract_claims, "vlm_A": extract_markdown_claims, "vlm_B": extract_claims}
VLM_TO_OURS = {"none": "absent", "present": "present"}
B_CLASS = {"erythema": lambda js: int(js["erythema"] == "present"), "edema": lambda js: int(js["edema"] == "present"),
           "exudate": lambda js: ["none", "non_purulent", "purulent"].index(js["exudate"]),
           "infection": lambda js: int(js["infection_risk"] == "elevated")}
A_CLASS = {"erythema": lambda a: int(a["erythema"]["value"] == "present"), "edema": lambda a: int(a["edema"]["value"] == "present"),
           "exudate": lambda a: ["none", "non_purulent", "purulent"].index(a["exudate"]["value"]),
           "infection": lambda a: int(a["infection"]["band"] == "high concern")}


def fmt(m, d=2):
    v, (lo, hi) = m["value"], m["ci95"]
    return "n/a" if v != v else f"{v:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]"


def fmt_diff(m):
    return f"{m['value']:+.2f} [{m['ci95'][0]:+.2f}, {m['ci95'][1]:+.2f}]"


def b_attrs(js: dict) -> dict:
    return {"erythema": {"value": VLM_TO_OURS[js["erythema"]], "uncertain": False},
            "edema": {"value": VLM_TO_OURS[js["edema"]], "uncertain": False},
            "exudate": {"value": js["exudate"], "uncertain": False},
            "infection": {"value": js["infection_risk"]}}


def simulated_outputs(df) -> pd.DataFrame:
    inv = {"Existent": "present", "Non-existent": "none"}
    ex = {"Non-existent": "none", "Serous": "non_purulent", "Sanguineous": "non_purulent", "Purulent": "purulent",
          "Seropurulent": "purulent"}
    rng = np.random.default_rng(0)
    rows = []
    for run in ("run1", "run2", "run3"):
        sub = df if run == "run1" else df[df.split == "test"]
        for r in sub.itertuples():
            refuse = rng.random() < (0.3 if r.infection_risk == "High" else 0.02)
            rows.append({"image_name": r.image_name, "run": run, "condition": "A", "result_type": "succeeded",
                         "stop_reason": "refusal" if refuse else "end_turn", "text": "" if refuse else r.report})
            js = {"erythema": inv.get(r.erythema, "none"), "edema": inv.get(r.edema, "none"),
                  "exudate": ex.get(r.exudate, "none"), "infection_risk": "low" if r.infection_risk == "Low" else "elevated"}
            rows.append({"image_name": r.image_name, "run": run, "condition": "B", "result_type": "succeeded",
                         "stop_reason": "refusal" if refuse else "end_turn", "text": "" if refuse else json.dumps(js)})
    return pd.DataFrame(rows)


def outputs_for(vlm, df, run, cond):
    """Per df row: report text (None if no usable output), parsed B JSON, and status
    in {"ok", "refused", "failed"} (failed = errored, expired, truncated or invalid JSON)."""
    sub = vlm[(vlm.run == run) & (vlm.condition == cond)].set_index("image_name")
    texts, parsed, status = [], [], []
    for n in df.image_name:
        if n not in sub.index or sub.loc[n, "result_type"] != "succeeded":
            texts.append(None), parsed.append(None), status.append("failed")
            continue
        if sub.loc[n, "stop_reason"] == "refusal":
            texts.append(None), parsed.append(None), status.append("refused")
            continue
        if sub.loc[n, "stop_reason"] != "end_turn":
            texts.append(None), parsed.append(None), status.append("failed")
            continue
        t = sub.loc[n, "text"]
        if cond == "B":
            try:
                js = json.loads(t)
                texts.append(render(b_attrs(js))), parsed.append(js), status.append("ok")
            except (json.JSONDecodeError, KeyError, TypeError):
                texts.append(None), parsed.append(None), status.append("failed")
        else:
            texts.append(t), parsed.append(None), status.append("ok")
    return texts, parsed, np.array(status)


def missing_counts(df, status, attrs=MAIN_ATTRS) -> np.ndarray:
    """Expert-labeled attributes of images without a usable report (counted as incorrect)."""
    out = np.zeros(len(df))
    for i in np.where(status != "ok")[0]:
        ref = expert_reference(df.iloc[i])
        out[i] = sum(ref[a] is not None for a in attrs)
    return out


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
    tpl_attrs = [json.loads(a) for a in tpl.attributes]
    vlm = simulated_outputs(df) if args.simulate else pd.read_parquet(OUT / "vlm" / "vlm_outputs.parquet")
    out_dir = OUT / ("vlm_simulated" if args.simulate else "vlm")
    out_dir.mkdir(parents=True, exist_ok=True)

    subsets = {"excl_900plus": np.where(lab.source_900plus == 0)[0], "all": np.arange(len(df)),
               "official_test": np.where(df.split == "test")[0]}
    texts, status, parsed_B = {"template": tpl.template_report.tolist()}, {"template": np.array(["ok"] * len(df))}, None
    texts["vlm_A"], _, status["vlm_A"] = outputs_for(vlm, df, "run1", "A")
    texts["vlm_B"], parsed_B, status["vlm_B"] = outputs_for(vlm, df, "run1", "B")
    S = {k: score_reports(v, [None] * len(df), df, extractor=EXTRACTOR[k]) for k, v in texts.items()}
    C = {k: claim_counts(S[k], len(df)) for k in SETS}
    M = {k: missing_counts(df, status[k]) for k in SETS}
    Cv = {k: claim_counts(S[k], len(df), attributes=VALIDATED_ATTRS) for k in SETS}
    Mv = {k: missing_counts(df, status[k], VALIDATED_ATTRS) for k in SETS}
    val_path = OUT / "markdown_validation.json"
    validation = json.loads(val_path.read_text()) if val_path.exists() else None
    metrics = {"status_counts": {k: dict(zip(*np.unique(status[k], return_counts=True))) for k in SETS}}
    if "input_tokens" in vlm and vlm.input_tokens.notna().any():
        metrics["tokens"] = {"input": int(vlm.input_tokens.sum()), "output": int(vlm.output_tokens.sum()),
                             "cost_usd_batch": float((vlm.input_tokens.sum() * 2 + vlm.output_tokens.sum() * 10) / 1e6)}

    md = ["# Phase 5: VLM baseline vs grounded template reports\n",
          "All report sets are scored by the same claim checker against the SurgWound expert labels.\n",
          "- **Correctness** = supported / (supported + contradicted). **Primary: refusals and failed requests counted as "
          "incorrect** (every expert-labeled attribute of that image counts as an incorrect claim). Secondary: excluded.",
          "- **Claims contradicting surgeon labels** = contradicted claims / all extracted claims, on produced reports only. Most contradictions are threshold disagreements, not invented findings (see REPORT.md).",
          "- **Unverifiable** = claims on attributes whose expert label is Uncertain.",
          "- Condition A (markdown reports) is read with the section-aware extractor (`src/report/markdown_claims.py`); "
          "template and condition B with the prose extractor. Condition A's checker was validated against hand labels on "
          "30 random reports; headline comparisons use only the attributes where it agrees at 0.96 or above "
          f"({', '.join(VALIDATED_ATTRS)}).\n"]
    if validation:
        md.append("### Checker validation on condition A (30 hand-labeled reports)\n")
        md.append("| extractor | attribute | n | agreement | wrong value | missed |")
        md.append("|---|---|---|---|---|---|")
        for r in validation["per_attribute"]:
            md.append(f"| {r['extractor']} | {r['attribute']} | {r['n']} | {r['agreement']:.2f} | {r['wrong']:.2f} | {r['missed']:.2f} |")
        for r in validation["overall"]:
            md.append(f"| {r['extractor']} | all | {r['n']} | {r['agreement']:.2f} | {r['wrong']:.2f} | {r['missed']:.2f} |")
        md.append("")

    # ---- refusals
    md.append("## Refusals and failed requests (run 1)\n")
    md.append("| condition | refused | failed | ok |")
    md.append("|---|---|---|---|")
    for k in ("vlm_A", "vlm_B"):
        c = metrics["status_counts"][k]
        md.append(f"| {k} | {c.get('refused', 0)} | {c.get('failed', 0)} | {c.get('ok', 0)} |")
    md.append("\nRefusals by expert infection risk and exudate class (all 686 images, run 1):\n")
    md.append("| condition | label | class | n images | refused | refused share |")
    md.append("|---|---|---|---|---|---|")
    metrics["refusals_by_label"] = {}
    for k in ("vlm_A", "vlm_B"):
        for col in ("infection_risk", "exudate"):
            vals = df[col].fillna("Uncertain")
            for cls in sorted(vals.unique(), key=lambda v: ["Low", "Medium", "High", "Non-existent", "Serous",
                                                            "Sanguineous", "Purulent", "Seropurulent", "Uncertain"].index(v)):
                m = (vals == cls).to_numpy()
                r = int((status[k][m] == "refused").sum())
                metrics["refusals_by_label"].setdefault(k, {}).setdefault(col, {})[cls] = {"n": int(m.sum()), "refused": r}
                md.append(f"| {k} | {col} | {cls} | {m.sum()} | {r} | {r / m.sum():.3f} |")

    # ---- headline: validated attributes only
    md.append("\n## Headline: claims on erythema, edema and infection only (checker validated on all three sets)\n")
    md.append("| subset | report set | n images | claims per report | correctness (primary: refusals incorrect) | claims contradicting surgeon labels | reports with a contradiction |")
    md.append("|---|---|---|---|---|---|---|")
    for s, idx in subsets.items():
        metrics.setdefault("rates_validated", {})[s] = {}
        for k in SETS:
            ok = idx[status[k][idx] == "ok"]
            prim = group_bootstrap(lambda ix, c=Cv[k][idx], m_=Mv[k][idx]: rates(c[ix], m_[ix]), len(idx), G[idx], n_boot, seed)
            sec = group_bootstrap(lambda ix, c=Cv[k][ok]: rates(c[ix]), len(ok), G[ok], n_boot, seed)
            metrics["rates_validated"][s][k] = {"n": len(idx), "primary": prim, "refusals_excluded": sec}
            md.append(f"| {s} | {k} | {len(idx)} | {fmt(sec['claims_per_report'], 1)} | {fmt(prim['correctness'])} | "
                      f"{fmt(sec['contradiction_rate'])} | {fmt(sec['reports_with_contradiction'])} |")
    md.append("\nPaired differences vs template, validated attributes (same group resamples):\n")
    md.append("| subset | comparison | correctness diff (primary) | contradicting-claims diff |")
    md.append("|---|---|---|---|")
    for s, idx in subsets.items():
        for k in ("vlm_A", "vlm_B"):
            ca, ma, ct = Cv[k][idx], Mv[k][idx], Cv["template"][idx]
            dc = group_bootstrap(lambda ix: {"d": rates(ca[ix], ma[ix])["correctness"] - rates(ct[ix])["correctness"]},
                                 len(idx), G[idx], n_boot, seed)["d"]
            dh = group_bootstrap(lambda ix: {"d": rates(ca[ix])["contradiction_rate"] - rates(ct[ix])["contradiction_rate"]},
                                 len(idx), G[idx], n_boot, seed)["d"]
            metrics.setdefault("paired_vs_template_validated", {}).setdefault(s, {})[k] = {"correctness": dc, "contradiction_rate": dh}
            md.append(f"| {s} | {k} minus template | {fmt_diff(dc)} | {fmt_diff(dh)} |")

    # ---- claim-level comparison
    md.append("\n## All attributes (exudate and healing included; condition A checker agreement there is 0.73 and 0.76)\n")
    md.append("| subset | report set | n images | reports produced | claims per report | correctness (primary: refusals incorrect) | correctness (refusals excluded) | claims contradicting surgeon labels | reports with a contradiction | unverifiable share |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for s, idx in subsets.items():
        metrics.setdefault("rates", {})[s] = {}
        for k in SETS:
            ok = idx[status[k][idx] == "ok"]
            prim = group_bootstrap(lambda ix, c=C[k][idx], m_=M[k][idx]: rates(c[ix], m_[ix]), len(idx), G[idx], n_boot, seed)
            sec = group_bootstrap(lambda ix, c=C[k][ok]: rates(c[ix]), len(ok), G[ok], n_boot, seed)
            metrics["rates"][s][k] = {"n": len(idx), "n_ok": len(ok), "primary": prim, "refusals_excluded": sec}
            md.append(f"| {s} | {k} | {len(idx)} | {len(ok)} | {fmt(sec['claims_per_report'], 1)} | {fmt(prim['correctness'])} | "
                      f"{fmt(sec['correctness'])} | {fmt(sec['contradiction_rate'])} | {fmt(sec['reports_with_contradiction'])} | "
                      f"{fmt(sec['unverifiable_share'])} |")
    md.append("\nPaired differences vs template on the same group resamples (correctness primary; contradicting claims on images where the VLM produced a report):\n")
    md.append("| subset | comparison | correctness diff (primary) | contradicting-claims diff |")
    md.append("|---|---|---|---|")
    for s, idx in subsets.items():
        for k in ("vlm_A", "vlm_B"):
            ca, ma, ct = C[k][idx], M[k][idx], C["template"][idx]
            dc = group_bootstrap(lambda ix: {"d": rates(ca[ix], ma[ix])["correctness"] - rates(ct[ix])["correctness"]},
                                 len(idx), G[idx], n_boot, seed)["d"]
            ok = idx[status[k][idx] == "ok"]
            cao, cto = C[k][ok], C["template"][ok]
            dh = group_bootstrap(lambda ix: {"d": rates(cao[ix])["contradiction_rate"] - rates(cto[ix])["contradiction_rate"]},
                                 len(ok), G[ok], n_boot, seed)["d"]
            metrics.setdefault("paired_vs_template", {}).setdefault(s, {})[k] = {"correctness": dc, "contradiction_rate": dh}
            md.append(f"| {s} | {k} minus template | {fmt_diff(dc)} | {fmt_diff(dh)} |")

    md.append("\n### Correctness by attribute (excluding ID 900+, produced reports)\n")
    md.append("| attribute | " + " | ".join(f"{k} claims | {k} correct" for k in SETS) + " |")
    md.append("|---|" + "---|---|" * len(SETS))
    per = {}
    for k in SETS:
        e = S[k][(S[k].against == "expert") & S[k].i.isin(subsets["excl_900plus"]) & S[k].status.isin(["supported", "contradicted"])]
        per[k] = e.groupby("attribute").status.agg(n="size", correct=lambda x: (x == "supported").mean())
    for a in ("erythema", "edema", "exudate", "infection", "infection_level", "healing"):
        cells = []
        for k in SETS:
            cells += ([str(int(per[k].loc[a, "n"])), f"{per[k].loc[a, 'correct']:.2f}"] if a in per[k].index else ["0", "n/a"])
        md.append(f"| {a} | " + " | ".join(cells) + " |")

    # ---- condition B as a classifier
    md.append("\n## Condition B as a zero-shot classifier vs model A (excluding ID 900+)\n")
    md.append("Primary: a refused or failed VLM request counts as a missed finding (negative class; for infection, a "
              "missed Elevated case). Model A uses its tuned decision rule; for infection it is the flag (high-concern band). "
              "Hard decisions, group-bootstrap CIs, paired difference on the same images.\n")
    md.append("| head | n | macro F1 VLM-B (primary) | macro F1 VLM-B (refusals excluded) | macro F1 model A | diff VLM-B minus A (primary) | critical recall VLM-B | critical recall model A |")
    md.append("|---|---|---|---|---|---|---|---|")
    base = np.zeros(len(df), bool)
    base[subsets["excl_900plus"]] = True
    for k_h, h in enumerate(HEAD_NAMES):
        idx = np.where(base & (Y[:, k_h] >= 0))[0]
        k = len(HEADS[h]["classes"])
        y = Y[idx, k_h]
        pv = np.array([B_CLASS[h](parsed_B[i]) if parsed_B[i] is not None else 0 for i in idx])
        pa = np.array([A_CLASS[h](tpl_attrs[i]) for i in idx])
        rv, sv = cluster_bootstrap(y, np.eye(k)[pv], G[idx], k, CRITICAL_CLASS[h], n_boot, seed, pred=pv)
        ra, sa = cluster_bootstrap(y, np.eye(k)[pa], G[idx], k, CRITICAL_CLASS[h], n_boot, seed, pred=pa)
        okm = np.array([parsed_B[i] is not None for i in idx])
        rx, _ = cluster_bootstrap(y[okm], np.eye(k)[pv[okm]], G[idx][okm], k, CRITICAL_CLASS[h], n_boot, seed, pred=pv[okm])
        d = paired_diff_ci(sv, sa, "macro_f1")
        metrics.setdefault("classifier", {})[h] = {"n": len(idx), "vlm_B_primary": rv, "vlm_B_refusals_excluded": rx,
                                                   "model_A": ra, "diff_macro_f1_primary": d}
        md.append(f"| {h} | {len(idx)} | {fmt(rv['macro_f1'])} | {fmt(rx['macro_f1'])} | {fmt(ra['macro_f1'])} | "
                  f"{d['mean_diff']:+.2f} [{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}] | {fmt(rv['critical_recall'])} | {fmt(ra['critical_recall'])} |")

    md.append("\n### Infection: Elevated recall and false alarms per 100 at each system's decision (excluding ID 900+)\n")
    md.append("The VLM gives a single label with no score, so its decision **cannot be threshold-tuned**; it is compared at its "
              "native decision. Model A is shown at the chosen operating point (flag, and flag or refer).\n")
    md.append("| system | Elevated recall | High-risk caught | false alarms per 100 | flagged per 100 |")
    md.append("|---|---|---|---|---|")
    idx = subsets["excl_900plus"]
    y = Y[idx, HEAD_NAMES.index("infection")]
    hi = lab.infection_high.to_numpy()[idx] == 1
    systems = {
        "VLM-B native decision (refusals = missed, primary)": np.array([B_CLASS["infection"](parsed_B[i]) if parsed_B[i] is not None else 0 for i in idx]),
        "model A, flag (high-concern band)": np.array([int(tpl_attrs[i]["infection"]["band"] == "high concern") for i in idx]),
        "model A, flag or refer (high-concern or uncertain band)": np.array([int(tpl_attrs[i]["infection"]["band"] != "low concern") for i in idx]),
    }
    okb = np.array([parsed_B[i] is not None for i in idx])
    for name, dsys in systems.items():
        def stat(ix, d_=dsys):
            yy, dd, hh = y[ix], d_[ix], hi[ix]
            return {"recall": dd[yy == 1].mean() if (yy == 1).any() else np.nan,
                    "high": dd[hh].mean() if hh.any() else np.nan,
                    "fa100": 100 * ((dd == 1) & (yy == 0)).mean(), "flag100": 100 * dd.mean()}
        b = group_bootstrap(stat, len(idx), G[idx], n_boot, seed)
        metrics.setdefault("infection_operating", {})[name] = b
        md.append(f"| {name} | {fmt(b['recall'])} | {fmt(b['high'])} (n={hi.sum()}) | {fmt(b['fa100'], 1)} | {fmt(b['flag100'], 1)} |")
    yb = y[okb]
    db = systems["VLM-B native decision (refusals = missed, primary)"][okb]
    metrics["infection_operating"]["VLM-B refusals excluded"] = {
        "n": int(okb.sum()), "recall": float(db[yb == 1].mean()) if (yb == 1).any() else None,
        "fa100": float(100 * ((db == 1) & (yb == 0)).mean())}
    md.append(f"\nVLM-B with refusals excluded (n = {okb.sum()}): Elevated recall "
              f"{metrics['infection_operating']['VLM-B refusals excluded']['recall']:.2f}, false alarms per 100 "
              f"{metrics['infection_operating']['VLM-B refusals excluded']['fa100']:.1f}.")

    # ---- run-to-run variation (only if the repeat runs exist)
    if not {"run2", "run3"} <= set(vlm.run.unique()):
        md.append("\n## Run-to-run variation\n")
        md.append("Not measured. The two repeat runs on the official test split were dropped to keep the batch under the "
                  "$15 budget (projected $20.64 for the full plan at effort low, $14.75 without repeats).")
        metrics["runs"] = "not run (budget)"
        return finish(md, metrics, S, texts, status, df, lab, out_dir, seed)
    md.append("\n## Run-to-run variation (official test split, 3 runs)\n")
    test = subsets["official_test"]
    md.append("| condition | run | refused | correctness (primary) | correctness (refusals excluded) | claims contradicting surgeon labels |")
    md.append("|---|---|---|---|---|---|")
    per_run = {}
    for cond in ("A", "B"):
        for run in ("run1", "run2", "run3"):
            t, p, st = outputs_for(vlm, df, run, cond)
            Sr = score_reports(t, [None] * len(df), df)
            Cr, Mr = claim_counts(Sr, len(df)), missing_counts(df, st)
            ok = test[st[test] == "ok"]
            prim = group_bootstrap(lambda ix: rates(Cr[test][ix], Mr[test][ix]), len(test), G[test], n_boot, seed)
            sec = group_bootstrap(lambda ix: rates(Cr[ok][ix]), len(ok), G[ok], n_boot, seed)
            metrics.setdefault("runs", {}).setdefault(cond, {})[run] = {"refused": int((st[test] == "refused").sum()),
                                                                        "primary": prim, "refusals_excluded": sec}
            md.append(f"| {cond} | {run} | {(st[test] == 'refused').sum()} | {fmt(prim['correctness'])} | "
                      f"{fmt(sec['correctness'])} | {fmt(sec['contradiction_rate'])} |")
            per_run[(cond, run)] = {i: ({(c.attribute, c.value) for c in extract_claims(t[i])} if t[i] else None) for i in test}
            if cond == "B":
                per_run[("Bjson", run)] = {i: p[i] for i in test}
    md.append("\nAgreement across the 3 runs (share of test images, among those with output in all three runs, where all three agree):\n")
    md.append("| condition | attribute | agreement |")
    md.append("|---|---|---|")
    for a in ("erythema", "edema", "exudate", "infection"):
        same = [len({frozenset(x for x in v if x[0] == a) for v in vals}) == 1
                for i in test if not any((vals := [per_run[("A", r)][i] for r in ("run1", "run2", "run3")]) is None for _ in [0])
                and all(v is not None for v in vals)]
        metrics.setdefault("agreement", {}).setdefault("A", {})[a] = float(np.mean(same)) if same else None
        md.append(f"| A (claims extracted from free text) | {a} | {np.mean(same):.2f} (n={len(same)}) |")
    for key in ("erythema", "edema", "exudate", "infection_risk"):
        vals_all = [[per_run[("Bjson", r)][i] for r in ("run1", "run2", "run3")] for i in test]
        same = [len({v[key] for v in vals}) == 1 for vals in vals_all if all(v is not None for v in vals)]
        metrics.setdefault("agreement", {}).setdefault("B", {})[key] = float(np.mean(same)) if same else None
        md.append(f"| B (structured) | {key} | {np.mean(same):.2f} (n={len(same)}) |")
    return finish(md, metrics, S, texts, status, df, lab, out_dir, seed)


def finish(md, metrics, S, texts, status, df, lab, out_dir, seed):
    """Concrete condition-A contradictions, then write all outputs."""
    md.append("\n## Examples: condition A contradicting the expert labels\n")
    md.append(f"Drawn at random from contradicted claims on the validated attributes ({', '.join(VALIDATED_ATTRS)}), at most "
              "three per attribute, so each example reflects the report text rather than a checker error. Clauses phrased "
              "as \"minimal or none\" / \"mild to none\" are skipped here (they were labeled unclear in the checker "
              "validation); they still count in the scores.\n")
    ex = S["vlm_A"][(S["vlm_A"].against == "expert") & (S["vlm_A"].status == "contradicted")
                    & S["vlm_A"].attribute.isin(VALIDATED_ATTRS)]
    ambiguous = r"\b(?:minimal|mild|slight)\s+(?:or|to)\s+(?:none|no)\b"
    picked, seen = [], {}
    for _, r in ex.sample(frac=1.0, random_state=seed).iterrows():
        if seen.get(r.attribute, 0) >= 3 or r.i in [p[0] for p in picked]:
            continue
        clause_i = next((c.text for c in extract_markdown_claims(texts["vlm_A"][r.i])
                         if c.attribute == r.attribute and c.value == r.value), "")
        if re.search(ambiguous, clause_i, flags=re.I):
            continue
        picked.append((r.i, r.attribute, r.value, r.reference))
        seen[r.attribute] = seen.get(r.attribute, 0) + 1
        if len(picked) == 8:
            break
    examples = []
    for i, a, v, ref in picked:
        row = df.iloc[i]
        clause = next((c.text for c in extract_markdown_claims(texts["vlm_A"][i]) if c.attribute == a and c.value == v), "")
        exp = expert_reference(row)
        examples.append({"image_name": row.image_name, "attribute": a, "vlm_claim": v, "expert_label": ref,
                         "clause": clause, "source_900plus": int(lab.source_900plus[i])})
        md.append(f"- **{row.image_name}**{' (ID 900+)' if lab.source_900plus[i] else ''}: {a} claimed **{v}**, expert label "
                  f"**{ref}**. Model text: \"{clause.strip()[:220]}\" (expert labels: erythema {exp['erythema']}, edema "
                  f"{exp['edema']}, exudate {exp['exudate']}, infection {exp['infection']})")
    metrics["examples"] = examples
    save_json(metrics, out_dir / "metrics.json")
    pd.DataFrame({"image_name": df.image_name, "status_A": status["vlm_A"], "vlm_A": texts["vlm_A"],
                  "status_B": status["vlm_B"], "vlm_B_rendered": texts["vlm_B"]}).to_parquet(out_dir / "reports.parquet", index=False)
    (out_dir / "comparison.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
