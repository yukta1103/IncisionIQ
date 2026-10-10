"""Phase 5 VLM baseline: Claude Opus 5.5, zero-shot, via the Message Batches API.

Two conditions, separate requests:
  A  free-text report, using the SurgWound report-task instruction verbatim
  B  structured attributes (JSON schema restricted to our label options),
     later rendered with our own template generator

Runs: every image once (primary protocol), plus two repeats on the 137
official-test images (run-to-run variation).

Data handling (see README): only inpainted images are sent, re-encoded as JPEG
from raw pixels (no EXIF or other metadata), long side at most 1024 px, with a
generic prompt. No file names, IDs or labels are sent; each request carries a
random opaque custom_id whose mapping to image names stays on this machine
(data/processed/vlm/, gitignored). Base64 images are used instead of the Files
API so nothing is stored on Anthropic's side beyond the standard request
retention. Batches are deleted after results are downloaded.

Usage:
  python scripts/phase5_vlm.py prepare      # build images and request files, no API calls
  python scripts/phase5_vlm.py pilot        # 2 synchronous requests to measure real token use
  python scripts/phase5_vlm.py submit       # create the batches
  python scripts/phase5_vlm.py collect      # poll, download, map back, delete batches
"""
import base64
import io
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.inpaint import inpaint_image, overlay_boxes  # noqa: E402
from src.utils import ROOT, save_json  # noqa: E402

MODEL = "claude-opus-5-5"
EFFORT = "medium"  # the model's default, set explicitly
MAX_SIDE = 1024
JPEG_QUALITY = 90
SEED = 42
PROC = ROOT / "data" / "processed"
WORK = PROC / "vlm"                      # local only (gitignored): images, id map, raw results
OUT = ROOT / "results" / "phase5" / "vlm"  # committed: parsed outputs keyed by image name

# Condition A: the SurgWound report-task instruction, verbatim
PROMPT_A = ("Given a surgical wound image, generate a detailed medical report that includes the following aspects: "
            "wound location, wound status, closure method, exudate characteristics, presence of erythema, presence of "
            "edema, urgency level, infection risk assessment.")

# Condition B: our attributes and exactly our label options
PROMPT_B = ("Given a surgical wound image, assess the following attributes and answer with one of the listed options "
            "for each.\n"
            "- erythema (redness around the wound): none | present\n"
            "- edema (swelling): none | present\n"
            "- exudate (drainage): none | non_purulent (serous or sanguineous) | purulent (purulent or seropurulent)\n"
            "- infection_risk: low | elevated (medium or high)")
SCHEMA_B = {
    "type": "object",
    "properties": {
        "erythema": {"type": "string", "enum": ["none", "present"]},
        "edema": {"type": "string", "enum": ["none", "present"]},
        "exudate": {"type": "string", "enum": ["none", "non_purulent", "purulent"]},
        "infection_risk": {"type": "string", "enum": ["low", "elevated"]},
    },
    "required": ["erythema", "edema", "exudate", "infection_risk"],
    "additionalProperties": False,
}
RUNS = {"run1": "all", "run2": "test", "run3": "test"}
MAX_BATCH_BYTES = 200 * 1024 * 1024  # stay well under the 256 MB batch limit


def _client():
    """Anthropic client. The key comes from ANTHROPIC_API_KEY or, if unset, from a
    gitignored .env file in the repo root (line ANTHROPIC_API_KEY=...). The key is
    never printed or written anywhere else."""
    import os

    import anthropic

    env = ROOT / ".env"
    if not os.environ.get("ANTHROPIC_API_KEY") and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            if k.strip() == "ANTHROPIC_API_KEY" and v.strip():
                os.environ["ANTHROPIC_API_KEY"] = v.strip().strip('"').strip("'")
    return anthropic.Anthropic()


def encode_image(name: str, boxes) -> bytes:
    with Image.open(PROC / "images" / name) as im:
        clean = inpaint_image(im, boxes)
    s = min(1.0, MAX_SIDE / max(clean.size))
    if s < 1.0:
        clean = clean.resize((round(clean.width * s), round(clean.height * s)), Image.LANCZOS)
    fresh = Image.fromarray(np.asarray(clean.convert("RGB")))  # raw pixels only, no metadata carried over
    buf = io.BytesIO()
    fresh.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buf.getvalue()


def request_params(cond: str, b64: str) -> dict:
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
               {"type": "text", "text": PROMPT_A if cond == "A" else PROMPT_B}]
    params = {"model": MODEL, "max_tokens": 8000 if cond == "A" else 4000,
              "messages": [{"role": "user", "content": content}],
              "output_config": {"effort": EFFORT}}
    if cond == "B":
        params["output_config"]["format"] = {"type": "json_schema", "schema": SCHEMA_B}
    return params


def prepare():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "images").mkdir(exist_ok=True)
    df = pd.read_parquet(PROC / "surgwound.parquet")
    boxes = overlay_boxes(PROC / "ocr.json", PROC / "orange_boxes.json")
    rng = random.Random(SEED)
    sizes = {}
    for n in df.image_name:
        data = encode_image(n, boxes[n])
        (WORK / "images" / n).write_bytes(data)
        sizes[n] = len(data)
    rows = []
    for run, scope in RUNS.items():
        names = df.image_name if scope == "all" else df.image_name[df.split == "test"]
        for cond in ("A", "B"):
            for n in names:
                rows.append({"custom_id": f"r{rng.getrandbits(64):016x}", "image_name": n, "run": run, "condition": cond})
    idmap = pd.DataFrame(rows)
    idmap.to_csv(WORK / "id_map.csv", index=False)  # local only
    # verify the encoded images carry no metadata
    with Image.open(WORK / "images" / df.image_name[0]) as im:
        meta = {"exif": bool(im.info.get("exif")), "keys": sorted(im.info.keys())}
    b64_total = sum(4 * ((sizes[n] + 2) // 3) for n in idmap.image_name)
    report = {"n_requests": len(idmap), "per_run_condition": idmap.groupby(["run", "condition"]).size().to_dict(),
              "jpeg_bytes_median": int(np.median(list(sizes.values()))), "jpeg_bytes_max": int(max(sizes.values())),
              "total_base64_mb": round(b64_total / 2**20, 1), "metadata_check_first_image": meta}
    report["per_run_condition"] = {f"{k[0]}/{k[1]}": v for k, v in report["per_run_condition"].items()}
    print(json.dumps(report, indent=1))
    return report


def load_requests():
    idmap = pd.read_csv(WORK / "id_map.csv")
    for r in idmap.itertuples():
        b64 = base64.standard_b64encode((WORK / "images" / r.image_name).read_bytes()).decode()
        yield r, {"custom_id": r.custom_id, "params": request_params(r.condition, b64)}


def pilot():
    client = _client()
    out = []
    for i, (r, req) in enumerate(load_requests()):
        if r.run != "run1" or r.image_name not in ("714.jpg", "943.jpg"):
            continue
        msg = client.messages.create(**req["params"])
        u = msg.usage
        out.append({"condition": r.condition, "stop_reason": msg.stop_reason, "input_tokens": u.input_tokens,
                    "output_tokens": u.output_tokens})
        print(out[-1])
    n = pd.read_csv(WORK / "id_map.csv").groupby("condition").size().to_dict()
    est = 0.0
    for c in ("A", "B"):
        rows = [o for o in out if o["condition"] == c]
        if rows:
            inp, outp = np.mean([o["input_tokens"] for o in rows]), np.mean([o["output_tokens"] for o in rows])
            est += n[c] * (inp * 2.0 + outp * 10.0) / 1e6  # Batch API: half of $4 / $20 per MTok
    print(f"estimated batch cost for all {sum(n.values())} requests: ${est:.2f}")
    save_json({"pilot": out, "estimated_batch_cost_usd": est}, WORK / "pilot.json")


def submit():
    client = _client()
    batches, cur, cur_bytes = [], [], 0
    for _, req in load_requests():
        size = len(json.dumps(req))
        if cur and cur_bytes + size > MAX_BATCH_BYTES:
            batches.append(cur)
            cur, cur_bytes = [], 0
        cur.append(req)
        cur_bytes += size
    batches.append(cur)
    ids = []
    for chunk in batches:
        b = client.messages.batches.create(requests=chunk)
        ids.append(b.id)
        print("created", b.id, len(chunk), "requests")
    save_json({"batch_ids": ids, "created": time.strftime("%Y-%m-%d %H:%M:%S")}, WORK / "batches.json")


def collect():
    client = _client()
    ids = json.loads((WORK / "batches.json").read_text())["batch_ids"]
    idmap = pd.read_csv(WORK / "id_map.csv").set_index("custom_id")
    for bid in ids:
        while client.messages.batches.retrieve(bid).processing_status != "ended":
            time.sleep(60)
    rows = []
    for bid in ids:
        for res in client.messages.batches.results(bid):
            meta = idmap.loc[res.custom_id]
            row = {"image_name": meta.image_name, "run": meta.run, "condition": meta.condition,
                   "result_type": res.result.type, "stop_reason": None, "text": None,
                   "input_tokens": None, "output_tokens": None}
            if res.result.type == "succeeded":
                msg = res.result.message
                row.update(stop_reason=msg.stop_reason,
                           text="".join(b.text for b in msg.content if b.type == "text"),
                           input_tokens=msg.usage.input_tokens, output_tokens=msg.usage.output_tokens)
            rows.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame(rows).sort_values(["run", "condition", "image_name"])
    out.to_parquet(OUT / "vlm_outputs.parquet", index=False)
    print(out.groupby(["run", "condition", "result_type"]).size())
    print("stop reasons:", out.stop_reason.value_counts(dropna=False).to_dict())
    print("tokens in/out:", int(out.input_tokens.sum()), int(out.output_tokens.sum()),
          f"-> about ${(out.input_tokens.sum() * 2 + out.output_tokens.sum() * 10) / 1e6:.2f} at batch prices")
    for bid in ids:  # data minimization: remove batches once results are stored locally
        client.messages.batches.delete(bid)
        print("deleted", bid)


if __name__ == "__main__":
    {"prepare": prepare, "pilot": pilot, "submit": submit, "collect": collect}[sys.argv[1]]()
