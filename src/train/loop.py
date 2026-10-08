"""Train one multi-task model on given indices, select the epoch with the lowest
inner-validation loss, and return logits for any requested evaluation indices."""
import math
import time

import numpy as np
import torch
from torch.utils.data import DataLoader

from src.data.dataset import WoundDataset, build_transforms
from src.data.labels import HEAD_NAMES, HEADS
from src.models.multitask import MaskedMultiTaskLoss, MultiTaskNet


def class_weights(labels: np.ndarray, idx: np.ndarray, power: float) -> dict[str, torch.Tensor]:
    """Inverse-frequency weights raised to `power` (0.5 = sqrt), normalized to mean 1."""
    out = {}
    for k, h in enumerate(HEAD_NAMES):
        y = labels[idx, k]
        y = y[y >= 0]
        n_c = np.bincount(y, minlength=len(HEADS[h]["classes"])).astype(float)
        w = (len(y) / np.maximum(n_c, 1)) ** power
        out[h] = torch.tensor(w / w.mean(), dtype=torch.float32)
    return out


@torch.no_grad()
def predict(model, images, labels, idx, cfg, device, return_features=False):
    model.eval()
    ds = WoundDataset(images, labels, idx, build_transforms(cfg, train=False))
    dl = DataLoader(ds, batch_size=cfg["eval_batch_size"], shuffle=False, num_workers=0)
    logits = {h: [] for h in HEAD_NAMES}
    feats = []
    for x, _, _ in dl:
        with torch.autocast("cuda", dtype=torch.float16, enabled=device == "cuda"):
            out, f = model(x.to(device), return_features=True)
        for h in HEAD_NAMES:
            logits[h].append(out[h].float().cpu())
        feats.append(f.float().cpu())
    logits = {h: torch.cat(v).numpy() for h, v in logits.items()}
    return (logits, torch.cat(feats).numpy()) if return_features else logits


def _lr_lambda(epoch_float, warmup, total):
    if epoch_float < warmup:
        return epoch_float / warmup
    p = (epoch_float - warmup) / max(1e-8, total - warmup)
    return 0.5 * (1 + math.cos(math.pi * p))


def train_model(images, labels, train_idx, val_idx, cfg, device, seed, log=print):
    torch.manual_seed(seed)
    np.random.seed(seed)
    tc = cfg["train"]
    model = MultiTaskNet(cfg["backbone"], {h: len(HEADS[h]["classes"]) for h in HEAD_NAMES},
                         pretrained=True, drop=tc["head_dropout"],
                         drop_path=tc.get("drop_path", 0.0)).to(device)
    crit = MaskedMultiTaskLoss(class_weights(labels, train_idx, tc["class_weight_power"]), tc["focal_gamma"])
    params = [
        {"params": model.backbone.parameters(), "lr": tc["lr_backbone"]},
        {"params": model.heads.parameters(), "lr": tc["lr_head"]},
    ]
    opt = torch.optim.AdamW(params, weight_decay=tc["weight_decay"])
    g = torch.Generator().manual_seed(seed)
    dl = DataLoader(WoundDataset(images, labels, train_idx, build_transforms(cfg, train=True)),
                    batch_size=tc["batch_size"], shuffle=True, drop_last=True, num_workers=0, generator=g)
    steps_per_epoch = len(dl)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: _lr_lambda(s / steps_per_epoch, tc["warmup_epochs"], tc["epochs"]))
    scaler = torch.amp.GradScaler(enabled=device == "cuda")

    best = {"loss": float("inf"), "epoch": -1, "state": None}
    history = []
    for ep in range(tc["epochs"]):
        model.train()
        t0, run = time.time(), []
        for x, y, _ in dl:
            x, y = x.to(device, non_blocking=True), y.to(device)
            with torch.autocast("cuda", dtype=torch.float16, enabled=device == "cuda"):
                out = model(x)
            loss, _ = crit(out, y, HEAD_NAMES)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), tc["grad_clip"])
            scaler.step(opt)
            scaler.update()
            sched.step()
            run.append(loss.item())
        vlog = predict(model, images, labels, val_idx, cfg, device)
        vloss, vparts = crit({h: torch.from_numpy(v) for h, v in vlog.items()},
                             torch.as_tensor(labels[val_idx]), HEAD_NAMES)
        vloss = float(vloss)
        history.append({"epoch": ep, "train_loss": float(np.mean(run)), "val_loss": vloss, **{f"val_{h}": v for h, v in vparts.items()}})
        if vloss < best["loss"]:
            best = {"loss": vloss, "epoch": ep,
                    "state": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}}
        log(f"  ep {ep:02d} train {np.mean(run):.3f} val {vloss:.3f} ({time.time() - t0:.0f}s)")
    model.load_state_dict(best["state"])
    return model, best, history
