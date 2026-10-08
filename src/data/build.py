"""Pivot the raw SurgWound VQA/report JSON into one row per image.

Output:
  data/processed/images/<image_name>   original bytes, not re-encoded
  data/processed/surgwound.parquet     one row per image, one column per attribute
"""
import base64
import hashlib
import io
import json
from pathlib import Path

import pandas as pd
from PIL import Image

from src.data.schema import FIELD_TO_COL, SPLITS, URGENCY_SHORT


def load_raw_rows(raw_dir: Path) -> list[dict]:
    rows = []
    for split in SPLITS:
        for kind in ("question", "report"):
            path = raw_dir / f"{split}_{kind}.json"
            with open(path, encoding="utf-8") as f:
                for r in json.load(f):
                    r["split"] = split
                    rows.append(r)
    return rows


def build(raw_dir: Path, out_dir: Path) -> pd.DataFrame:
    img_dir = out_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    rows = load_raw_rows(raw_dir)
    records: dict[str, dict] = {}
    options: dict[str, list[str]] = {}

    for r in rows:
        name = r["image_name"]
        rec = records.get(name)
        if rec is None:
            raw = base64.b64decode(r["image"])
            with Image.open(io.BytesIO(raw)) as im:
                fmt, (w, h), mode = im.format, im.size, im.mode
            (img_dir / name).write_bytes(raw)
            rec = {
                "image_name": name,
                "split": r["split"],
                "sha256": hashlib.sha256(raw).hexdigest(),
                "format": fmt,
                "mode": mode,
                "width": w,
                "height": h,
                "n_bytes": len(raw),
            }
            records[name] = rec
        elif rec["split"] != r["split"]:
            # Recorded instead of raised so the audit can report it.
            rec.setdefault("other_splits", set()).add(r["split"])

        if r["task_type"] == "report_generation":
            rec["report"] = r["answer"]
            continue
        col = FIELD_TO_COL[r["field"]]
        ans = r["answer"]
        if col == "urgency":
            ans = URGENCY_SHORT[ans]
        rec[col] = ans
        options[col] = [URGENCY_SHORT.get(o, o) for o in r["options"]]

    df = pd.DataFrame(records.values())
    if "other_splits" in df:
        df["other_splits"] = df["other_splits"].apply(
            lambda s: ",".join(sorted(s)) if isinstance(s, set) else ""
        )
    df = df.sort_values(["split", "image_name"], key=lambda c: c.map(
        {s: i for i, s in enumerate(SPLITS)}) if c.name == "split" else c).reset_index(drop=True)
    df.to_parquet(out_dir / "surgwound.parquet", index=False)
    with open(out_dir / "options.json", "w") as f:
        json.dump(options, f, indent=2)
    return df
