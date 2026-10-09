## Primary: grouped 5-fold CV, pooled out-of-fold (tuned decision rule)

Infection: the ID 900+ excluded estimate comes first and is the primary honest estimate.

| head | subset | n | macro F1 FT | macro F1 baseline | diff (paired) | critical AUROC FT | critical AUROC baseline | diff (paired) |
|---|---|---|---|---|---|---|---|---|
| erythema (present) | all | 660 | 0.63 [0.59, 0.67] | 0.59 [0.55, 0.63] | +0.04 [-0.00, +0.08] | 0.70 [0.65, 0.74] | 0.64 [0.59, 0.69] | +0.06 [+0.01, +0.10] |
| erythema (present) | excl_900plus | 591 | 0.61 [0.57, 0.66] | 0.58 [0.54, 0.62] | +0.04 [-0.01, +0.08] | 0.68 [0.63, 0.73] | 0.63 [0.58, 0.69] | +0.04 [-0.01, +0.09] |
| edema (present) | all | 554 | 0.63 [0.58, 0.68] | 0.65 [0.60, 0.70] | -0.02 [-0.07, +0.02] | 0.74 [0.68, 0.79] | 0.75 [0.69, 0.81] | -0.01 [-0.05, +0.03] |
| edema (present) | excl_900plus | 497 | 0.65 [0.59, 0.71] | 0.66 [0.60, 0.72] | -0.01 [-0.06, +0.04] | 0.75 [0.68, 0.81] | 0.75 [0.68, 0.81] | -0.00 [-0.05, +0.05] |
| exudate (purulent) | all | 626 | 0.47 [0.41, 0.52] | 0.43 [0.39, 0.48] | +0.03 [-0.03, +0.10] | 0.74 [0.65, 0.83] | 0.76 [0.66, 0.84] | -0.01 [-0.14, +0.12] |
| exudate (purulent) | excl_900plus | 565 | 0.48 [0.41, 0.54] | 0.44 [0.39, 0.49] | +0.04 [-0.04, +0.11] | 0.76 [0.67, 0.84] | 0.77 [0.68, 0.85] | -0.02 [-0.15, +0.11] |
| infection (elevated) | excl_900plus | 613 | 0.62 [0.57, 0.66] | 0.65 [0.60, 0.70] | -0.03 [-0.08, +0.01] | 0.77 [0.71, 0.82] | 0.73 [0.67, 0.79] | +0.04 [-0.03, +0.11] |
| infection (elevated) | all | 686 | 0.64 [0.59, 0.68] | 0.69 [0.64, 0.73] | -0.05 [-0.09, -0.01] | 0.79 [0.74, 0.84] | 0.76 [0.71, 0.81] | +0.03 [-0.02, +0.08] |

| head | subset | critical recall FT | critical recall baseline | balanced acc FT | balanced acc baseline |
|---|---|---|---|---|---|
| erythema | excl_900plus | 0.50 [0.43, 0.58] | 0.55 [0.47, 0.63] | 0.62 [0.58, 0.67] | 0.60 [0.55, 0.65] |
| erythema | all | 0.56 [0.49, 0.63] | 0.59 [0.51, 0.66] | 0.64 [0.60, 0.68] | 0.61 [0.57, 0.66] |
| edema | excl_900plus | 0.53 [0.38, 0.66] | 0.50 [0.38, 0.61] | 0.68 [0.61, 0.75] | 0.68 [0.62, 0.74] |
| edema | all | 0.56 [0.43, 0.67] | 0.56 [0.45, 0.66] | 0.68 [0.61, 0.74] | 0.69 [0.63, 0.74] |
| exudate | excl_900plus | 0.10 [0.00, 0.22] | 0.28 [0.12, 0.45] | 0.48 [0.42, 0.54] | 0.48 [0.41, 0.54] |
| exudate | all | 0.10 [0.00, 0.21] | 0.27 [0.12, 0.43] | 0.47 [0.42, 0.52] | 0.47 [0.41, 0.54] |
| infection | excl_900plus | 0.50 [0.40, 0.61] | 0.44 [0.34, 0.54] | 0.66 [0.60, 0.71] | 0.66 [0.61, 0.72] |
| infection | all | 0.58 [0.49, 0.67] | 0.55 [0.46, 0.65] | 0.68 [0.64, 0.73] | 0.71 [0.66, 0.76] |

High-risk images predicted elevated (excl_900plus, n High = 12): fine-tuned 0.67 [0.36, 0.92], baseline 0.67 [0.36, 0.92]

High-risk images predicted elevated (all, n High = 23): fine-tuned 0.83 [0.67, 0.96], baseline 0.83 [0.65, 0.96]

For reference, plain argmax macro F1 (FT / baseline, all): erythema 0.63 / 0.60, edema 0.61 / 0.65, exudate 0.45 / 0.46, infection 0.67 / 0.67

## Secondary: official test minus leaked images (tuned decision rule)

Infection: the ID 900+ excluded estimate comes first and is the primary honest estimate.

| head | subset | n | macro F1 FT | macro F1 baseline | diff (paired) | critical AUROC FT | critical AUROC baseline | diff (paired) |
|---|---|---|---|---|---|---|---|---|
| erythema (present) | all | 118 | 0.59 [0.49, 0.69] | 0.61 [0.51, 0.71] | -0.02 [-0.16, +0.12] | 0.74 [0.61, 0.84] | 0.74 [0.63, 0.84] | -0.01 [-0.12, +0.11] |
| erythema (present) | excl_900plus | 108 | 0.53 [0.43, 0.64] | 0.59 [0.49, 0.68] | -0.06 [-0.19, +0.09] | 0.68 [0.56, 0.80] | 0.71 [0.59, 0.83] | -0.03 [-0.17, +0.11] |
| edema (present) | all | 102 | 0.51 [0.42, 0.62] | 0.65 [0.54, 0.75] | -0.14 [-0.27, -0.01] | 0.60 [0.46, 0.74] | 0.72 [0.59, 0.84] | -0.11 [-0.25, +0.01] |
| edema (present) | excl_900plus | 93 | 0.56 [0.45, 0.69] | 0.68 [0.55, 0.80] | -0.12 [-0.27, +0.04] | 0.63 [0.44, 0.79] | 0.74 [0.60, 0.87] | -0.12 [-0.28, +0.03] |
| exudate (purulent) | all | 113 | 0.34 [0.26, 0.43] | 0.53 [0.38, 0.67] | -0.19 [-0.35, -0.03] | 0.78 [0.68, 0.86] | 0.94 [0.88, 0.99] | -0.17 [-0.25, -0.09] |
| exudate (purulent) | excl_900plus | 102 | 0.33 [0.26, 0.42] | 0.57 [0.41, 0.71] | -0.23 [-0.39, -0.06] | 0.81 [0.72, 0.90] | 0.94 [0.88, 0.99] | -0.13 [-0.21, -0.06] |
| infection (elevated) | excl_900plus | 113 | 0.59 [0.47, 0.72] | 0.64 [0.52, 0.77] | -0.05 [-0.16, +0.04] | 0.74 [0.57, 0.90] | 0.74 [0.56, 0.90] | +0.00 [-0.13, +0.16] |
| infection (elevated) | all | 124 | 0.64 [0.52, 0.75] | 0.69 [0.57, 0.79] | -0.05 [-0.14, +0.04] | 0.79 [0.64, 0.92] | 0.80 [0.66, 0.92] | -0.01 [-0.11, +0.11] |

| head | subset | critical recall FT | critical recall baseline | balanced acc FT | balanced acc baseline |
|---|---|---|---|---|---|
| erythema | excl_900plus | 0.12 [0.00, 0.26] | 0.77 [0.60, 0.92] | 0.55 [0.49, 0.62] | 0.67 [0.57, 0.76] |
| erythema | all | 0.21 [0.08, 0.35] | 0.79 [0.64, 0.92] | 0.59 [0.53, 0.67] | 0.68 [0.58, 0.77] |
| edema | excl_900plus | 0.17 [0.00, 0.40] | 0.75 [0.47, 1.00] | 0.55 [0.46, 0.68] | 0.78 [0.63, 0.90] |
| edema | all | 0.14 [0.00, 0.33] | 0.79 [0.56, 1.00] | 0.51 [0.42, 0.62] | 0.76 [0.64, 0.87] |
| exudate | excl_900plus | 0.75 [0.00, 1.00] | 0.50 [0.00, 1.00] | 0.49 [0.27, 0.64] | 0.67 [0.45, 0.89] |
| exudate | all | 0.75 [0.00, 1.00] | 0.50 [0.00, 1.00] | 0.50 [0.29, 0.65] | 0.61 [0.40, 0.82] |
| infection | excl_900plus | 0.36 [0.09, 0.69] | 0.55 [0.25, 0.86] | 0.62 [0.47, 0.78] | 0.70 [0.54, 0.86] |
| infection | all | 0.50 [0.22, 0.76] | 0.69 [0.44, 0.91] | 0.68 [0.53, 0.81] | 0.76 [0.63, 0.88] |

High-risk images predicted elevated (excl_900plus, n High = 2): fine-tuned 0.50 [0.00, 1.00], baseline 1.00 [1.00, 1.00]

High-risk images predicted elevated (all, n High = 5): fine-tuned 0.80 [0.33, 1.00], baseline 1.00 [1.00, 1.00]

For reference, plain argmax macro F1 (FT / baseline, all): erythema 0.59 / 0.69, edema 0.45 / 0.49, exudate 0.49 / 0.62, infection 0.65 / 0.75

## Learned decision-rule alphas (0 = argmax, 1 = full prior correction)

| model | split | erythema | edema | exudate | infection |
|---|---|---|---|---|---|
| fine-tuned | cv0 | 0.60 | 0.25 | 0.10 | 0.15 |
| fine-tuned | cv1 | 0.90 | 0.05 | 0.00 | 1.40 |
| fine-tuned | cv2 | 0.00 | 0.05 | 0.05 | 0.05 |
| fine-tuned | cv3 | 0.10 | 0.50 | 0.20 | 0.30 |
| fine-tuned | cv4 | 0.25 | 0.15 | 0.00 | 0.10 |
| fine-tuned | secondary | 0.05 | 0.30 | 0.70 | 0.05 |
| frozen + logreg | cv0 | 0.05 | 0.05 | 1.40 | 0.05 |
| frozen + logreg | cv1 | 0.00 | 0.00 | 0.05 | 0.00 |
| frozen + logreg | cv2 | 0.55 | 0.00 | 0.80 | 0.10 |
| frozen + logreg | cv3 | 0.15 | 0.45 | 0.00 | 0.00 |
| frozen + logreg | cv4 | 0.95 | 0.00 | 0.40 | 0.30 |
| frozen + logreg | secondary | 0.85 | 0.60 | 0.35 | 0.35 |

## Source probe (ID 900+ vs rest), grouped 5-fold CV

n = 686, positives = 73. Frozen pretrained features AUROC 0.93 [0.88, 0.96]; fine-tuned features AUROC 0.89 [0.83, 0.94].

## Per-fold macro F1 (fine-tuned, tuned rule)

|    |   erythema |   edema |   exudate |   infection |
|---:|-----------:|--------:|----------:|------------:|
|  0 |       0.61 |    0.66 |      0.65 |        0.61 |
|  1 |       0.74 |    0.61 |      0.41 |        0.59 |
|  2 |       0.6  |    0.62 |      0.53 |        0.63 |
|  3 |       0.61 |    0.56 |      0.41 |        0.71 |
|  4 |       0.59 |    0.67 |      0.44 |        0.63 |