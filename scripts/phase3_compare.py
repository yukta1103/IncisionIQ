"""Phase 3: before/after tables for the overlay mitigation.

Reads the Phase 2 (original images) and Phase 3 (inpainted images) outputs and
writes results/phase3/comparison.md. No computation beyond formatting; all
numbers come from metrics.json and shortcut_summary.json.

Usage: python scripts/phase3_compare.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.labels import CRITICAL_CLASS, HEAD_NAMES, HEADS  # noqa: E402
from src.utils import ROOT  # noqa: E402

RUNS = {"before (original images)": ("results/phase2/convnext_tiny_384", "results/phase3/convnext_tiny_384"),
        "after (overlays inpainted)": ("results/phase3/convnext_tiny_384_inpainted",
                                       "results/phase3/convnext_tiny_384_inpainted")}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def ci(m, signed=False):
    f = "{:+.3f}" if signed else "{:.2f}"
    return f"{f.format(m['value'])} [{f.format(m['ci95'][0])}, {f.format(m['ci95'][1])}]"


def main():
    data = {k: (load(f"{m}/metrics.json"), load(f"{s}/shortcut_summary.json")) for k, (m, s) in RUNS.items()}
    L = ["# Phase 3: overlay mitigation, before vs after\n",
         "Same folds, inner splits, seeds, candidate grid and decision rule. Only the input images differ.\n"]

    L.append("## Classifier metrics (grouped 5-fold CV, fine-tuned, tuned decision rule)\n")
    L.append("| head | subset | macro F1 before | macro F1 after | critical AUROC before | critical AUROC after |")
    L.append("|---|---|---|---|---|---|")
    for h in HEAD_NAMES:
        for s in (("excl_900plus", "all") if h == "infection" else ("all", "excl_900plus")):
            r = [data[k][0]["results"]["cv"]["tuned"]["finetuned"][s][h] for k in RUNS]
            L.append(f"| {h} ({HEADS[h]['classes'][CRITICAL_CLASS[h]]}) | {s} | {ci(r[0]['macro_f1'])} | {ci(r[1]['macro_f1'])} | "
                     f"{ci(r[0]['critical_auroc'])} | {ci(r[1]['critical_auroc'])} |")
    for s in ("excl_900plus", "all"):
        r = [data[k][0]["results"]["cv"]["tuned"]["finetuned"][s]["infection"] for k in RUNS]
        L.append(f"\nHigh-risk recall ({s}, n High = {r[0]['n_high']}): before {ci(r[0]['critical_recall_subset'])}, "
                 f"after {ci(r[1]['critical_recall_subset'])}")
    L.append("\nFrozen-feature baseline, infection critical AUROC (all / excl. 900+): " + "; ".join(
        f"{k}: {ci(data[k][0]['results']['cv']['tuned']['baseline']['all']['infection']['critical_auroc'])} / "
        f"{ci(data[k][0]['results']['cv']['tuned']['baseline']['excl_900plus']['infection']['critical_auroc'])}" for k in RUNS))

    L.append("\n## Source probe: AUROC for predicting ID 900+ from image features\n")
    L.append("| features | before | after |")
    L.append("|---|---|---|")
    for key, label in (("frozen_pretrained", "frozen pretrained ConvNeXt-Tiny"), ("finetuned_cv_models", "fine-tuned (CV fold models)")):
        L.append(f"| {label} | " + " | ".join(ci(data[k][0]["source_probe"][key]["auroc"]) for k in RUNS) + " |")

    L.append("\n## Grad-CAM mass on overlay regions (overlay images only)\n")
    L.append("Excess = CAM mass share on overlay boxes minus their area share (0 means no preference). "
             "After mitigation the boxes mark where overlays used to be.\n")
    L.append("| head | subset | n | area share | CAM mass before | excess before | CAM mass after | excess after |")
    L.append("|---|---|---|---|---|---|---|---|")
    for h in HEAD_NAMES:
        for sub in ("all_overlay_images", "id_900plus", "other_sources"):
            b, a = (data[k][1]["cam"][h][sub] for k in RUNS)
            L.append(f"| {h} | {sub} | {b['n']} | {b['mean_overlay_area_frac']['value']:.3f} | "
                     f"{ci(b['mean_cam_mass_on_overlay'])} | {ci(b['mean_excess_mass'], True)} | "
                     f"{ci(a['mean_cam_mass_on_overlay'])} | {ci(a['mean_excess_mass'], True)} |")

    L.append("\n## Causal check: change in P(critical class) when overlays are inpainted at test time\n")
    L.append("Before: the original model, original vs inpainted input. After: the mitigated model on the same pair. "
             "Negative = overlays push toward the critical class.\n")
    L.append("| head | subset | n | mean dP before | flips before | mean dP after | flips after |")
    L.append("|---|---|---|---|---|---|---|")
    for h in HEAD_NAMES:
        for sub in ("all_overlay_images", "id_900plus", "other_sources"):
            b, a = (data[k][1]["occlusion"][h][sub] for k in RUNS)
            L.append(f"| {h} | {sub} | {b['n']} | {ci(b['mean_delta_p_critical'], True)} | {b['decision_flips']} | "
                     f"{ci(a['mean_delta_p_critical'], True)} | {a['decision_flips']} |")
    out = ROOT / "results" / "phase3" / "comparison.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
