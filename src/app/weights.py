"""Model files for the demo: download once, verify the SHA-256, cache.

src/app/weights.json lists every file the app needs at runtime, each with a pinned URL and
checksum:
  - the fold 0 wound model, a release asset of this repo (CC BY-SA 4.0);
  - the three EasyOCR models (text detector plus Chinese and Cyrillic recognizers), from the
    EasyOCR project's own versioned GitHub releases (Apache-2.0), fetched by us instead of by
    EasyOCR so the download has a timeout, retries and our checksum, and EasyOCR's own
    downloader stays off.
Lookup order for each file: the cache (INCISIONIQ_CACHE, default ~/.cache/incisioniq), then a
local copy (dist/ for the wound model), then a download into the cache that is verified before
it is moved into place. A file whose checksum does not match is never used.
"""
import hashlib
import json
import os
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((Path(__file__).parent / "weights.json").read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cache_dir() -> Path:
    return Path(os.environ.get("INCISIONIQ_CACHE", Path.home() / ".cache" / "incisioniq"))


def _download(url: str, dest: Path, retries: int, timeout: int):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r, open(dest, "wb") as f:
                for chunk in iter(lambda: r.read(1 << 20), b""):
                    f.write(chunk)
            return
        except OSError:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def fetch(url: str, filename: str, expected: str, dest_dir: Path, zip_member: str | None = None,
          local: Path | None = None, retries: int = 3, timeout: int = 60) -> Path:
    """Return a verified copy of `filename` in dest_dir, downloading it if needed. With
    zip_member, the URL is a zip archive and that member is extracted (and verified)."""
    target = dest_dir / filename
    for cand in (target, local):
        if cand is not None and cand.exists() and sha256(cand) == expected:
            return cand
    dest_dir.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(".part")
    try:
        _download(url, part, retries, timeout)
        if zip_member:
            with zipfile.ZipFile(part) as z, z.open(zip_member) as src, open(target.with_suffix(".unzip"), "wb") as out:
                for chunk in iter(lambda: src.read(1 << 20), b""):
                    out.write(chunk)
            part.unlink()
            part = target.with_suffix(".unzip")
        got = sha256(part)
        if got != expected:
            raise RuntimeError(f"checksum mismatch for {url}: expected {expected}, got {got}")
        part.replace(target)
    finally:
        for leftover in (target.with_suffix(".part"), target.with_suffix(".unzip")):
            leftover.unlink(missing_ok=True)
    return target


def weights_path(spec: dict = SPEC) -> Path:
    """The verified wound-model weights file."""
    return fetch(spec["url"], spec["filename"], spec["sha256"], cache_dir(), local=ROOT / "dist" / spec["filename"])


def ocr_models_dir(spec: dict = SPEC) -> Path:
    """A directory holding the verified EasyOCR models, for easyocr.Reader(model_storage_directory=...)."""
    d = cache_dir() / "easyocr"
    for m in spec["ocr_models"]:
        fetch(m["url"], m["filename"], m["sha256"], d, zip_member=m["filename"])
    return d
