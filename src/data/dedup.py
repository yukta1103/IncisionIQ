"""Near-duplicate detection.

Primary signal: 64-bit pHash, compared against both the original and the
horizontally mirrored version of every other image (reposts are often flipped).
Secondary signal: cosine similarity of self-supervised DINOv2 embeddings, which
survives crops, borders and filters that break pHash. The secondary signal only
nominates candidates; it is not used to group images without visual review.
"""
from pathlib import Path

import imagehash
import numpy as np
from PIL import Image, ImageOps


def phash_table(paths: list[Path]) -> tuple[np.ndarray, np.ndarray]:
    """Return (hashes, mirrored_hashes) as uint8 bit arrays of shape (N, 64)."""
    hs, hm = [], []
    for p in paths:
        with Image.open(p) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            hs.append(imagehash.phash(im).hash.flatten())
            hm.append(imagehash.phash(ImageOps.mirror(im)).hash.flatten())
    return np.array(hs, dtype=np.uint8), np.array(hm, dtype=np.uint8)


def hamming_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a.astype(np.int16)
    b = b.astype(np.int16)
    # popcount of xor via dot products on {0,1} vectors
    return (a @ (1 - b).T + (1 - a) @ b.T).astype(np.int16)


def phash_distance(paths: list[Path]) -> np.ndarray:
    """Pairwise min(Hamming(original, original), Hamming(original, mirror))."""
    h, hm = phash_table(paths)
    d = np.minimum(hamming_matrix(h, h), hamming_matrix(h, hm))
    d = np.minimum(d, d.T)
    np.fill_diagonal(d, 64)
    return d


def embed(paths: list[Path], model_name: str, device: str, batch_size: int = 32) -> np.ndarray:
    import timm
    import torch

    model = timm.create_model(model_name, pretrained=True, num_classes=0).to(device).eval()
    cfg = timm.data.resolve_data_config({}, model=model)
    tf = timm.data.create_transform(**cfg)
    feats = []
    with torch.no_grad(), torch.autocast(device_type=device, dtype=torch.float16, enabled=device == "cuda"):
        for i in range(0, len(paths), batch_size):
            batch = []
            for p in paths[i:i + batch_size]:
                with Image.open(p) as im:
                    batch.append(tf(ImageOps.exif_transpose(im).convert("RGB")))
            f = model(torch.stack(batch).to(device)).float()
            feats.append(torch.nn.functional.normalize(f, dim=1).cpu().numpy())
    return np.concatenate(feats)


def clusters_from_pairs(n: int, pairs: list[tuple[int, int]]) -> list[list[int]]:
    """Union-find connected components with size > 1."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in pairs:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted((g for g in groups.values() if len(g) > 1), key=len, reverse=True)
