"""Redact caption text that the VLM transcribed from the images (Phase 7 audit).

OCR + inpainting missed some burned-in captions, and the free-text VLM reports
(condition A) quoted and translated them for 8 images. This script replaces the
quoted caption text, and its translation, with "[caption text redacted]" in
results/phase5/vlm/vlm_outputs.parquet. Downstream files are then regenerated:

    python scripts/phase7_redact_vlm_captions.py
    python scripts/phase5_compare.py
    python scripts/phase5_markdown_validation.py
    python scripts/phase5_checker_errors.py

The rule touches only lines that contain Chinese or Cyrillic characters (every
transcribed caption does; no other report text does), and the script checks that
afterwards no report contains such characters. It holds no caption text itself.
It is idempotent.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "phase5" / "vlm" / "vlm_outputs.parquet"

TAG = "[caption text redacted]"
AFFECTED = ["19.jpg", "20.jpg", "32.jpg", "85.jpg", "617.jpg", "718.jpg", "946.jpg", "978.jpg"]
NON_LATIN = re.compile(r"[Ѐ-ӿ　-〿一-鿿＀-￯]")

# (pattern, replacement), tried in order on a line with non-Latin characters; the first match wins
RULES = [
    # **Image annotation:** "..." (...)   /   **Image caption (Russian):** "..." = ...
    (re.compile(r"^(\*\*Image (?:annotation|caption[^*]*):\*\*).*$"), r"\1 " + TAG),
    # **Image context:** The overlaid caption reads "..." (...). The handwritten text ... label. Parts of ...
    (re.compile(r"^(\*\*Image context:\*\*) The overlaid caption reads .*?(Parts of the image.*)$"), r"\1 " + TAG + r". \2"),
    # **Image context:** The caption reads "..." ("..."). This is ...
    (re.compile(r"^(\*\*Image context:\*\*) The caption reads \".*?\" \(\".*?\"\)\.(.*)$"), r"\1 " + TAG + r".\2"),
    # **Image context:** The caption "..." means "...," so ...
    (re.compile(r"The caption \".*?\" means \".*?,\""), "The caption: " + TAG + ","),
    # The image caption (...) translates to "...," indicating ...
    (re.compile(r"The image caption \(.*?\) translates to \".*?,\""), "The image caption: " + TAG + ","),
]


def redact_text(text: str) -> tuple[str, int]:
    """Return the redacted text and the number of lines changed."""
    lines, n = text.split("\n"), 0
    for i, line in enumerate(lines):
        if not NON_LATIN.search(line):
            continue
        for pat, rep in RULES:
            new = pat.sub(rep, line)
            if new != line:
                lines[i], n = new, n + 1
                break
    return "\n".join(lines), n


def main():
    df = pd.read_parquet(OUT)
    changed = {}
    for i, row in df.iterrows():
        if isinstance(row.text, str):
            new, n = redact_text(row.text)
            if n:
                df.at[i, "text"] = new
                changed[row.image_name] = changed.get(row.image_name, 0) + n
    left = [r.image_name for r in df.itertuples() if isinstance(r.text, str) and NON_LATIN.search(r.text)]
    assert not left, f"non-Latin text left in: {left}"
    assert set(changed) <= set(AFFECTED), f"unexpected reports changed: {set(changed) - set(AFFECTED)}"
    df.to_parquet(OUT, index=False)
    print(f"redacted {sum(changed.values())} line(s) in {len(changed)} report(s): {sorted(changed)}"
          if changed else "nothing to redact (already redacted)")


if __name__ == "__main__":
    main()
