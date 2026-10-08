"""In-memory image dataset.

All 686 images are letterboxed (padded to square, never cropped, so the wound is
not cut off) and cached as uint8 tensors at `cache_size`. Augmentation runs on
those tensors. Color augmentation is deliberately mild because redness is a
diagnostic signal: no hue shift, small brightness/contrast/saturation changes.
"""
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps
from torch.utils.data import Dataset
from torchvision.transforms import v2

PAD_RGB = (124, 116, 104)  # ImageNet mean, so padding normalizes to about zero
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def letterbox(im: Image.Image, size: int) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    s = max(im.size)
    canvas = Image.new("RGB", (s, s), PAD_RGB)
    canvas.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    return canvas.resize((size, size), Image.BICUBIC)


def load_cache(img_dir: Path, names, size: int, cache_file: Path) -> torch.Tensor:
    if cache_file.exists():
        data = torch.load(cache_file)
        if data["names"] == list(names) and data["size"] == size:
            return data["images"]
    imgs = []
    for n in names:
        with Image.open(img_dir / n) as im:
            imgs.append(torch.from_numpy(np.asarray(letterbox(im, size))).permute(2, 0, 1).contiguous())
    images = torch.stack(imgs)
    torch.save({"names": list(names), "size": size, "images": images}, cache_file)
    return images


def build_transforms(cfg: dict, train: bool):
    size = cfg["input_size"]
    norm = [v2.ToDtype(torch.float32, scale=True), v2.Normalize(MEAN, STD)]
    if not train:
        return v2.Compose([v2.Resize(size, antialias=True), *norm])
    a = cfg["augment"]
    return v2.Compose([
        v2.RandomResizedCrop(size, scale=tuple(a["crop_scale"]), ratio=(0.8, 1.25), antialias=True),
        v2.RandomHorizontalFlip(),
        v2.RandomVerticalFlip(),
        v2.RandomRotation(a["rotation"], fill=list(PAD_RGB)),
        v2.ColorJitter(brightness=a["brightness"], contrast=a["contrast"], saturation=a["saturation"], hue=0.0),
        *norm,
    ])


class WoundDataset(Dataset):
    def __init__(self, images: torch.Tensor, labels: np.ndarray, idx: np.ndarray, transform):
        self.images, self.labels, self.idx, self.tf = images, labels, idx, transform

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, i):
        j = self.idx[i]
        return self.tf(self.images[j]), torch.as_tensor(self.labels[j], dtype=torch.long), j
