"""Validate claim extraction on VLM condition A reports against hand labels.

30 reports drawn at random (seed 2026, results/phase5/markdown_validation_sample.json,
excluding 8 reports already seen during development). For each report and
attribute, the hand label records what the VLM text asserts (not what the
expert label is): healing, exudate, erythema, edema, infection, or "unclear"
when the text is genuinely ambiguous. Labels were written from the raw report
sections before looking at any extractor output for these reports
(results/phase5/markdown_validation_labels.csv).

Reports, per extractor and attribute (unclear excluded):
  agreement   extracted value equals the hand label (one value, matching)
  wrong       a value was extracted that differs from the hand label
  missed      no value extracted

Usage: python scripts/phase5_markdown_validation.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.report.claims import claims_by_attribute, extract_claims  # noqa: E402
from src.report.markdown_claims import extract_markdown_claims  # noqa: E402
from src.utils import ROOT, save_json  # noqa: E402

ATTRS = ["healing", "exudate", "erythema", "edema", "infection"]
OUT = ROOT / "results" / "phase5"


def main():
    labels = pd.read_csv(OUT / "markdown_validation_labels.csv")
    sample = json.loads((OUT / "markdown_validation_sample.json").read_text())["images"]
    assert sorted(labels.image_name) == sorted(sample), "labels must cover exactly the sample"
    vlm = pd.read_parquet(OUT / "vlm" / "vlm_outputs.parquet").query("condition == 'A' and run == 'run1'").set_index("image_name")
    rows = []
    for r in labels.itertuples():
        text = vlm.loc[r.image_name, "text"]
        got = {"markdown": claims_by_attribute(extract_markdown_claims(text)), "prose": claims_by_attribute(extract_claims(text))}
        for a in ATTRS:
            lab = getattr(r, a)
            for ex, g in got.items():
                vals = g.get(a, set())
                rows.append({"image_name": r.image_name, "attribute": a, "label": lab, "extractor": ex,
                             "extracted": "|".join(sorted(vals)),
                             "agree": lab != "unclear" and vals == {lab},
                             "wrong": lab != "unclear" and bool(vals - {lab}),
                             "missed": lab != "unclear" and not vals})
    R = pd.DataFrame(rows)
    R.to_csv(OUT / "markdown_validation_results.csv", index=False)
    L = R[R.label != "unclear"]
    tab = L.groupby(["extractor", "attribute"]).agg(n=("agree", "size"), agreement=("agree", "mean"),
                                                    wrong=("wrong", "mean"), missed=("missed", "mean")).round(3)
    overall = L.groupby("extractor").agg(n=("agree", "size"), agreement=("agree", "mean"), wrong=("wrong", "mean"),
                                         missed=("missed", "mean")).round(3)
    n_unclear = int((labels[ATTRS] == "unclear").sum().sum())
    save_json({"per_attribute": tab.reset_index().to_dict("records"), "overall": overall.reset_index().to_dict("records"),
               "n_reports": len(labels), "n_unclear_labels": n_unclear}, OUT / "markdown_validation.json")
    print(f"reports: {len(labels)}, attribute labels: {len(labels) * len(ATTRS)}, unclear (excluded): {n_unclear}\n")
    print(overall.to_string(), "\n")
    print(tab.to_string())
    print("\nmarkdown extractor disagreements:")
    print(L[(L.extractor == "markdown") & ~L.agree][["image_name", "attribute", "label", "extracted"]].to_string(index=False))


if __name__ == "__main__":
    main()
