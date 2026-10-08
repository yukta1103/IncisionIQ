## Primary: grouped 5-fold CV, pooled out-of-fold (tuned decision rule)

Infection: the ID 900+ excluded estimate comes first and is the primary honest estimate.

| head | subset | n | macro F1 FT | macro F1 baseline | diff (paired) | critical AUROC FT | critical AUROC baseline | diff (paired) |
|---|---|---|---|---|---|---|---|---|
| erythema (present) | all | 660 | 0.62 [0.58, 0.66] | 0.59 [0.56, 0.63] | +0.03 [-0.01, +0.07] | 0.71 [0.67, 0.75] | 0.64 [0.59, 0.69] | +0.07 [+0.03, +0.12] |
| erythema (present) | excl_900plus | 591 | 0.61 [0.57, 0.65] | 0.58 [0.54, 0.63] | +0.02 [-0.02, +0.07] | 0.69 [0.65, 0.74] | 0.63 [0.57, 0.69] | +0.06 [+0.01, +0.11] |
| edema (present) | all | 554 | 0.63 [0.58, 0.68] | 0.63 [0.58, 0.67] | +0.01 [-0.03, +0.05] | 0.76 [0.70, 0.81] | 0.74 [0.68, 0.80] | +0.02 [-0.03, +0.07] |
| edema (present) | excl_900plus | 497 | 0.65 [0.59, 0.70] | 0.63 [0.58, 0.68] | +0.02 [-0.03, +0.06] | 0.77 [0.70, 0.83] | 0.74 [0.67, 0.80] | +0.03 [-0.02, +0.08] |
| exudate (purulent) | all | 626 | 0.43 [0.38, 0.48] | 0.44 [0.39, 0.49] | -0.01 [-0.07, +0.05] | 0.76 [0.68, 0.83] | 0.72 [0.61, 0.82] | +0.04 [-0.10, +0.17] |
| exudate (purulent) | excl_900plus | 565 | 0.43 [0.38, 0.48] | 0.45 [0.40, 0.50] | -0.02 [-0.08, +0.05] | 0.77 [0.69, 0.84] | 0.74 [0.64, 0.84] | +0.02 [-0.10, +0.16] |
| infection (elevated) | excl_900plus | 613 | 0.66 [0.61, 0.71] | 0.63 [0.58, 0.68] | +0.03 [-0.02, +0.08] | 0.77 [0.71, 0.82] | 0.74 [0.67, 0.80] | +0.03 [-0.03, +0.10] |
| infection (elevated) | all | 686 | 0.69 [0.64, 0.73] | 0.66 [0.62, 0.71] | +0.02 [-0.02, +0.07] | 0.80 [0.75, 0.84] | 0.77 [0.72, 0.82] | +0.03 [-0.02, +0.08] |

| head | subset | critical recall FT | critical recall baseline | balanced acc FT | balanced acc baseline |
|---|---|---|---|---|---|
| erythema | excl_900plus | 0.48 [0.40, 0.56] | 0.55 [0.47, 0.63] | 0.61 [0.57, 0.66] | 0.60 [0.56, 0.65] |
| erythema | all | 0.54 [0.47, 0.61] | 0.59 [0.51, 0.66] | 0.63 [0.59, 0.67] | 0.62 [0.57, 0.66] |
| edema | excl_900plus | 0.53 [0.40, 0.65] | 0.50 [0.39, 0.61] | 0.68 [0.62, 0.74] | 0.66 [0.60, 0.72] |
| edema | all | 0.57 [0.45, 0.68] | 0.56 [0.45, 0.67] | 0.68 [0.62, 0.74] | 0.67 [0.62, 0.73] |
| exudate | excl_900plus | 0.03 [0.00, 0.11] | 0.31 [0.15, 0.48] | 0.45 [0.40, 0.50] | 0.49 [0.42, 0.56] |
| exudate | all | 0.03 [0.00, 0.11] | 0.30 [0.13, 0.47] | 0.45 [0.40, 0.50] | 0.48 [0.42, 0.55] |
| infection | excl_900plus | 0.43 [0.33, 0.53] | 0.48 [0.36, 0.59] | 0.67 [0.62, 0.72] | 0.66 [0.60, 0.72] |
| infection | all | 0.52 [0.43, 0.62] | 0.58 [0.48, 0.68] | 0.70 [0.65, 0.75] | 0.70 [0.65, 0.75] |

High-risk images predicted elevated (excl_900plus, n High = 12): fine-tuned 0.42 [0.13, 0.70], baseline 0.67 [0.36, 0.92]

High-risk images predicted elevated (all, n High = 23): fine-tuned 0.70 [0.48, 0.88], baseline 0.83 [0.65, 0.96]

For reference, plain argmax macro F1 (FT / baseline, all): erythema 0.64 / 0.60, edema 0.61 / 0.64, exudate 0.43 / 0.45, infection 0.69 / 0.69

## Secondary: official test minus leaked images (tuned decision rule)

Infection: the ID 900+ excluded estimate comes first and is the primary honest estimate.

| head | subset | n | macro F1 FT | macro F1 baseline | diff (paired) | critical AUROC FT | critical AUROC baseline | diff (paired) |
|---|---|---|---|---|---|---|---|---|
| erythema (present) | all | 118 | 0.62 [0.53, 0.71] | 0.60 [0.50, 0.69] | +0.03 [-0.08, +0.14] | 0.72 [0.60, 0.83] | 0.73 [0.61, 0.83] | -0.01 [-0.12, +0.10] |
| erythema (present) | excl_900plus | 108 | 0.60 [0.51, 0.69] | 0.58 [0.48, 0.68] | +0.02 [-0.09, +0.13] | 0.67 [0.55, 0.79] | 0.69 [0.56, 0.81] | -0.02 [-0.16, +0.12] |
| edema (present) | all | 102 | 0.57 [0.46, 0.69] | 0.65 [0.54, 0.75] | -0.08 [-0.21, +0.05] | 0.62 [0.48, 0.75] | 0.72 [0.60, 0.84] | -0.10 [-0.22, +0.02] |
| edema (present) | excl_900plus | 93 | 0.60 [0.45, 0.74] | 0.68 [0.55, 0.80] | -0.08 [-0.24, +0.08] | 0.63 [0.45, 0.79] | 0.75 [0.60, 0.88] | -0.12 [-0.26, +0.02] |
| exudate (purulent) | all | 113 | 0.44 [0.31, 0.54] | 0.40 [0.30, 0.50] | +0.03 [-0.12, +0.19] | 0.80 [0.67, 0.94] | 0.92 [0.80, 1.00] | -0.12 [-0.20, -0.04] |
| exudate (purulent) | excl_900plus | 102 | 0.47 [0.32, 0.58] | 0.42 [0.31, 0.53] | +0.05 [-0.12, +0.22] | 0.83 [0.70, 0.96] | 0.93 [0.83, 1.00] | -0.09 [-0.18, -0.02] |
| infection (elevated) | excl_900plus | 113 | 0.65 [0.49, 0.78] | 0.61 [0.50, 0.73] | +0.03 [-0.09, +0.14] | 0.72 [0.53, 0.90] | 0.75 [0.57, 0.91] | -0.04 [-0.18, +0.11] |
| infection (elevated) | all | 124 | 0.72 [0.59, 0.82] | 0.66 [0.55, 0.76] | +0.06 [-0.03, +0.15] | 0.79 [0.62, 0.92] | 0.81 [0.67, 0.93] | -0.02 [-0.13, +0.07] |

| head | subset | critical recall FT | critical recall baseline | balanced acc FT | balanced acc baseline |
|---|---|---|---|---|---|
| erythema | excl_900plus | 0.62 [0.43, 0.80] | 0.77 [0.60, 0.92] | 0.64 [0.54, 0.74] | 0.66 [0.56, 0.75] |
| erythema | all | 0.67 [0.50, 0.83] | 0.79 [0.64, 0.92] | 0.66 [0.56, 0.75] | 0.66 [0.57, 0.75] |
| edema | excl_900plus | 0.25 [0.00, 0.55] | 0.75 [0.47, 1.00] | 0.59 [0.46, 0.73] | 0.78 [0.63, 0.90] |
| edema | all | 0.29 [0.07, 0.54] | 0.79 [0.56, 1.00] | 0.57 [0.46, 0.71] | 0.76 [0.64, 0.87] |
| exudate | excl_900plus | 0.00 [0.00, 0.00] | 0.75 [0.00, 1.00] | 0.44 [0.33, 0.57] | 0.66 [0.42, 0.82] |
| exudate | all | 0.00 [0.00, 0.00] | 0.75 [0.00, 1.00] | 0.41 [0.33, 0.54] | 0.64 [0.42, 0.79] |
| infection | excl_900plus | 0.36 [0.08, 0.67] | 0.55 [0.25, 0.86] | 0.65 [0.50, 0.80] | 0.68 [0.52, 0.85] |
| infection | all | 0.56 [0.29, 0.81] | 0.69 [0.44, 0.91] | 0.73 [0.60, 0.86] | 0.74 [0.61, 0.86] |

High-risk images predicted elevated (excl_900plus, n High = 2): fine-tuned 1.00 [1.00, 1.00], baseline 1.00 [1.00, 1.00]

High-risk images predicted elevated (all, n High = 5): fine-tuned 1.00 [1.00, 1.00], baseline 1.00 [1.00, 1.00]

For reference, plain argmax macro F1 (FT / baseline, all): erythema 0.62 / 0.65, edema 0.45 / 0.46, exudate 0.44 / 0.55, infection 0.72 / 0.74

## Learned decision-rule alphas (0 = argmax, 1 = full prior correction)

| model | split | erythema | edema | exudate | infection |
|---|---|---|---|---|---|
| fine-tuned | cv0 | 0.00 | 0.45 | 0.00 | 0.15 |
| fine-tuned | cv1 | 0.95 | 0.10 | 0.00 | 0.60 |
| fine-tuned | cv2 | 0.00 | 0.15 | 0.00 | 0.00 |
| fine-tuned | cv3 | 0.40 | 0.65 | 0.25 | 0.25 |
| fine-tuned | cv4 | 0.30 | 0.30 | 0.30 | 0.10 |
| fine-tuned | secondary | 1.00 | 0.40 | 0.00 | 0.00 |
| frozen + logreg | cv0 | 0.05 | 0.10 | 0.45 | 0.30 |
| frozen + logreg | cv1 | 0.30 | 0.00 | 0.65 | 0.10 |
| frozen + logreg | cv2 | 0.50 | 0.15 | 0.15 | 0.05 |
| frozen + logreg | cv3 | 0.15 | 0.10 | 0.00 | 0.05 |
| frozen + logreg | cv4 | 0.80 | 0.20 | 0.05 | 0.70 |
| frozen + logreg | secondary | 0.20 | 0.60 | 0.30 | 0.35 |

## Source probe (ID 900+ vs rest), grouped 5-fold CV

n = 686, positives = 73. Frozen pretrained features AUROC 0.93 [0.88, 0.97]; fine-tuned features AUROC 0.92 [0.88, 0.95].

## Per-fold macro F1 (fine-tuned, tuned rule)

|    |   erythema |   edema |   exudate |   infection |
|---:|-----------:|--------:|----------:|------------:|
|  0 |       0.67 |    0.65 |      0.42 |        0.66 |
|  1 |       0.69 |    0.63 |      0.46 |        0.76 |
|  2 |       0.64 |    0.66 |      0.52 |        0.68 |
|  3 |       0.6  |    0.57 |      0.38 |        0.7  |
|  4 |       0.52 |    0.63 |      0.39 |        0.61 |