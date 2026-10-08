import timm
import torch
from torch import nn


class MultiTaskNet(nn.Module):
    """Shared timm backbone with one linear head per attribute."""

    def __init__(self, backbone: str, head_sizes: dict[str, int], pretrained: bool = True, drop: float = 0.2,
                 drop_path: float = 0.0):
        super().__init__()
        self.backbone = timm.create_model(backbone, pretrained=pretrained, num_classes=0,
                                          drop_path_rate=drop_path)
        d = self.backbone.num_features
        self.heads = nn.ModuleDict({
            h: nn.Sequential(nn.Dropout(drop), nn.Linear(d, k)) for h, k in head_sizes.items()
        })

    def forward(self, x, return_features: bool = False):
        f = self.backbone(x)
        out = {h: m(f) for h, m in self.heads.items()}
        return (out, f) if return_features else out


class MaskedMultiTaskLoss(nn.Module):
    """Sum over heads of class-weighted (optionally focal) cross-entropy.
    Labels of -1 are masked out. Each head is averaged over its labeled samples."""

    def __init__(self, class_weights: dict[str, torch.Tensor], focal_gamma: float = 0.0):
        super().__init__()
        self.w = class_weights
        self.gamma = focal_gamma

    def forward(self, logits: dict, y: torch.Tensor, head_names: list[str]):
        total, parts = 0.0, {}
        for k, h in enumerate(head_names):
            m = y[:, k] >= 0
            if not m.any():
                continue
            lg, t = logits[h][m].float(), y[m, k]
            w = self.w[h].to(lg.device)
            ce = nn.functional.cross_entropy(lg, t, reduction="none")
            if self.gamma > 0:
                pt = torch.exp(-ce)
                ce = (1 - pt) ** self.gamma * ce
            loss = (w[t] * ce).sum() / w[t].sum()
            parts[h] = loss.item()
            total = total + loss
        return total, parts
