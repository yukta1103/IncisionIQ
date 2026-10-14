"""Direction of the claim checker's remaining errors, and a spot-check export.

On the 30 hand-labeled condition A reports (scripts/phase5_markdown_validation.py),
each (report, attribute) is scored against the surgeon label twice: once with
the hand label (what the report actually says) and once with the checker's
extraction. Disagreements are classified:
  false contradiction    checker says the report contradicts the surgeon label, the text does not
  missed contradiction   the text contradicts the surgeon label, the checker does not count it
  other                  e.g. both contradict but with different values, or one side states nothing
Hand labels marked "unclear" and attributes whose surgeon label is Uncertain are excluded.

The template and condition B are rendered by our own template; the checker's
faithfulness to their source JSON is 1.000 (tables.md), so there are no
extraction errors to classify for those two sets.

Writes results/phase5/checker_error_direction.json and
results/phase5/markdown_validation_export.md (each validation report with its
hand labels, checker output and surgeon labels, for manual spot-checks).

Usage: python scripts/phase5_checker_errors.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.report.claims import claims_by_attribute  # noqa: E402
from src.report.faithfulness import expert_reference  # noqa: E402
from src.report.markdown_claims import extract_markdown_claims  # noqa: E402
from src.utils import ROOT, save_json  # noqa: E402

ATTRS = ["erythema", "edema", "infection", "exudate", "healing"]
OUT = ROOT / "results" / "phase5"


def status(value, ref):
    if value is None:
        return "no_claim"
    return "supported" if value == ref else "contradicted"


def main():
    df = pd.read_parquet(ROOT / "data" / "processed" / "surgwound.parquet").set_index("image_name")
    labels = pd.read_csv(OUT / "markdown_validation_labels.csv").set_index("image_name")
    vlm = pd.read_parquet(OUT / "vlm" / "vlm_outputs.parquet").query("condition == 'A' and run == 'run1'").set_index("image_name")
    rows, export = [], ["# Condition A validation reports: hand labels vs checker output\n",
                        "For spot-checking. Hand label = what the report text asserts (\"unclear\" when ambiguous). "
                        "Checker = `src/report/markdown_claims.py`. Surgeon = SurgWound expert label "
                        "(None = Uncertain). Each report is shown in full as the VLM wrote it.\n"]
    for n, lab in labels.iterrows():
        text = vlm.loc[n, "text"]
        got = claims_by_attribute(extract_markdown_claims(text))
        ref = expert_reference(df.loc[n].to_dict() | {"image_name": n})
        table = ["| attribute | hand label | checker | surgeon | agreement |", "|---|---|---|---|---|"]
        for a in ATTRS:
            hand = lab[a]
            chk = "|".join(sorted(got.get(a, set()))) or "(none)"
            agree = "yes" if hand != "unclear" and got.get(a, set()) == {hand} else ("n/a" if hand == "unclear" else "NO")
            table.append(f"| {a} | {hand} | {chk} | {ref[a]} | {agree} |")
            if hand == "unclear" or ref[a] is None:
                continue
            vals = got.get(a, set())
            chk_val = next(iter(vals)) if len(vals) == 1 else (None if not vals else "multiple")
            s_hand, s_chk = status(hand, ref[a]), status(chk_val if chk_val != "multiple" else None, ref[a])
            if chk_val == "multiple":
                s_chk = "contradicted" if any(v != ref[a] for v in vals) else "supported"
            if s_hand == s_chk and (chk_val == hand):
                kind = "correct"
            elif s_chk == "contradicted" and s_hand == "supported":
                kind = "false_contradiction"
            elif s_hand == "contradicted" and s_chk != "contradicted":
                kind = "missed_contradiction"
            else:
                kind = "other"
            rows.append({"image_name": n, "attribute": a, "hand": hand, "checker": chk, "surgeon": ref[a], "kind": kind})
        export += [f"\n---\n\n## {n}\n", "\n".join(table), "\n<details><summary>Full report</summary>\n", text, "\n</details>\n"]
    R = pd.DataFrame(rows)
    tab = R.groupby(["attribute", "kind"]).size().unstack(fill_value=0)
    for c in ("correct", "false_contradiction", "missed_contradiction", "other"):
        if c not in tab:
            tab[c] = 0
    tab = tab[["correct", "false_contradiction", "missed_contradiction", "other"]]
    tab.loc["all"] = tab.sum()
    save_json({"report_set": "condition A (free text)", "per_attribute": tab.reset_index().to_dict("records"),
               "template_and_condition_B": "rendered by our template; checker faithfulness to source JSON 1.000, "
                                           "no extraction errors"}, OUT / "checker_error_direction.json")
    R.to_csv(OUT / "checker_error_direction.csv", index=False)
    (OUT / "markdown_validation_export.md").write_text("\n".join(export) + "\n", encoding="utf-8")
    print(tab.to_string())


if __name__ == "__main__":
    main()
