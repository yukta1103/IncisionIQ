"""Grouped splits.

Primary protocol: grouped 5-fold CV over all 686 images. Groups come from the
broad automatic same-patient rule of Phase 1, so no group spans two folds.
Each outer training portion is further split (grouped) into inner-train and
inner-val. Inner-val is used for checkpoint selection and, in Phase 4, for
temperature scaling. The outer fold is never seen during training or selection.

Secondary protocol: official test split minus test images with a verified
same-patient partner in train/val (and minus in-test exact duplicates).
Training uses official train+val minus every image that shares a broad-rule
group with any remaining test image.
"""
import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import StratifiedGroupKFold


def strat_key(lab: pd.DataFrame) -> np.ndarray:
    """Stratify on infection (binary) x exudate purulent, the two rarest signals."""
    return lab.infection.to_numpy() * 2 + (lab.exudate.to_numpy() == 2)


def outer_folds(lab, groups, n_splits, seed) -> np.ndarray:
    fold = np.full(len(lab), -1)
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for k, (_, te) in enumerate(sgkf.split(np.zeros(len(lab)), strat_key(lab), groups)):
        fold[te] = k
    return fold


def inner_split(idx, lab, groups, n_inner, seed) -> tuple[np.ndarray, np.ndarray]:
    """Return (inner_train_idx, inner_val_idx) as absolute indices."""
    sub = lab.iloc[idx]
    sgkf = StratifiedGroupKFold(n_splits=n_inner, shuffle=True, random_state=seed)
    tr, va = next(sgkf.split(np.zeros(len(idx)), strat_key(sub), groups[idx]))
    return idx[tr], idx[va]


def secondary_split(df, groups_broad, review_file) -> dict:
    review = yaml.safe_load(open(review_file, encoding="utf-8"))
    name_to_i = {n: i for i, n in enumerate(df.image_name)}
    split = df.split.to_numpy()

    removed = set()
    # verified same-patient groups that mix test with train/val: drop their test members
    for g in review["exact_or_near_identical"] + review["same_patient_verified"]:
        sp = {split[name_to_i[n]] for n in g}
        if "test" in sp and sp & {"train", "val"}:
            removed |= {n for n in g if split[name_to_i[n]] == "test"}
    # in-test exact duplicates: keep the first, drop the rest
    for g in review["exact_or_near_identical"]:
        test_members = [n for n in g if split[name_to_i[n]] == "test"]
        removed |= set(test_members[1:])

    test_idx = np.array([i for i, n in enumerate(df.image_name) if split[i] == "test" and n not in removed])
    test_groups = set(groups_broad[test_idx])
    train_idx = np.array([i for i in range(len(df))
                          if split[i] in ("train", "val") and groups_broad[i] not in test_groups])
    excluded_train = sorted(df.image_name[i] for i in range(len(df))
                            if split[i] in ("train", "val") and groups_broad[i] in test_groups)
    return {
        "train_idx": train_idx,
        "test_idx": test_idx,
        "removed_test": sorted(removed, key=lambda n: int(n.split(".")[0])),
        "excluded_train": excluded_train,
    }
