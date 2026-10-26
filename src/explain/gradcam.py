"""Grad-CAM for the multi-task model plus overlay-region geometry.

CAMs are computed at the model input resolution (letterboxed square), in fp32.
Overlay boxes are stored in original-image pixels by Phase 1; `to_letterbox`
maps them into model-input coordinates so CAM mass can be measured on them.
"""
import numpy as np
import torch
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from torch import nn


class HeadOutput(nn.Module):
    """Expose one head of MultiTaskNet as a plain logits model for pytorch-grad-cam."""

    def __init__(self, model, head):
        super().__init__()
        self.model, self.head = model, head

    def forward(self, x):
        return self.model(x)[self.head]


def gradcam_maps(model, x: torch.Tensor, head: str, target_class: int, batch_size: int = 16) -> np.ndarray:
    """Return CAMs of shape (N, H, W) in [0, 1] for `target_class` of `head`."""
    model.eval()
    wrapped = HeadOutput(model, head)
    out = []
    with GradCAM(model=wrapped, target_layers=[model.backbone.stages[-1]]) as cam:
        for i in range(0, len(x), batch_size):
            xb = x[i:i + batch_size]
            out.append(cam(input_tensor=xb, targets=[ClassifierOutputTarget(target_class)] * len(xb)))
    return np.concatenate(out)


def gradcam_raw(model, x: torch.Tensor, head: str, target_class: int) -> np.ndarray:
    """Unnormalized Grad-CAM (H, W) at input resolution for one image (x of shape (1, C, H, W)).

    Same formula as pytorch-grad-cam's GradCAM on the last ConvNeXt stage (weights = spatial mean
    of the gradients; ReLU of the weighted activation sum), but without its per-image min-max
    stretch, so maps from different images share one scale. The demo divides by a fixed constant
    (results/phase7/cam_scale.json) instead of stretching each map to full brightness.
    """
    model.eval()
    store = {}
    handle = model.backbone.stages[-1].register_forward_hook(lambda m, i, o: store.__setitem__("a", o))
    try:
        with torch.enable_grad():
            score = model(x)[head][0, target_class]
            grads = torch.autograd.grad(score, store["a"])[0]
    finally:
        handle.remove()
    a = store["a"].detach()
    cam = torch.relu((grads.mean(dim=(2, 3), keepdim=True) * a).sum(dim=1, keepdim=True))
    cam = torch.nn.functional.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)
    return cam[0, 0].float().cpu().numpy()


def letterbox_geometry(width: int, height: int, size: int) -> tuple[float, float, float]:
    """(scale, x_offset, y_offset) mapping original pixels to letterboxed `size` pixels."""
    s = max(width, height)
    scale = size / s
    return scale, (s - width) / 2 * scale, (s - height) / 2 * scale


def to_letterbox(boxes, width, height, size):
    scale, ox, oy = letterbox_geometry(width, height, size)
    return [[x0 * scale + ox, y0 * scale + oy, x1 * scale + ox, y1 * scale + oy] for x0, y0, x1, y1 in boxes]


def box_mask(boxes, size) -> np.ndarray:
    m = np.zeros((size, size), dtype=bool)
    for x0, y0, x1, y1 in boxes:
        m[max(0, int(np.floor(y0))):min(size, int(np.ceil(y1))), max(0, int(np.floor(x0))):min(size, int(np.ceil(x1)))] = True
    return m


def content_mask(width, height, size) -> np.ndarray:
    """True on real image pixels, False on letterbox padding."""
    scale, ox, oy = letterbox_geometry(width, height, size)
    return box_mask([[ox, oy, ox + width * scale, oy + height * scale]], size)


def mass_fraction(cam: np.ndarray, region: np.ndarray, content: np.ndarray) -> float:
    """Share of CAM mass (over real image pixels only) that falls inside `region`."""
    c = cam * content
    total = c.sum()
    return float((c * region).sum() / total) if total > 0 else np.nan
