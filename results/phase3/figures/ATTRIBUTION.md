# Attribution for the figures in this folder

## Source images

All photographs in these figures come from the **SurgWound** dataset:

> Xu, J., Yin, C., Chatzipanagiotou, O. P., Tsilimigras, D. I., Clear, K., Yao, B., Cao, W., Wang, D., Pawlik, T. M., and Zhang, P. *SurgWound-Bench: a benchmark for surgical wound diagnosis.* npj Digital Medicine (2026). doi:10.1038/s41746-026-02791-3

Dataset: Hugging Face `xuxuxuxuxu/SurgWound`, licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, https://creativecommons.org/licenses/by-sa/4.0/. The dataset authors collected the images from public social-media posts and had them labeled by surgeons at The Ohio State University Wexner Medical Center.

## These figures are adapted material

Changes made to the source images:
- letterboxed (padded to a square) and resized to 384 px,
- in the `*_inpainted_*` figures, detected text and redaction overlays were removed by inpainting,
- detected text and overlay regions are pixelated for display in every figure,
- Grad-CAM heat maps are overlaid on copies of each image.

As required by the ShareAlike term, **the figures in this folder are released under CC BY-SA 4.0**. This license applies to these figures only, not to the rest of the repository.

## Images shown

The same 12 images from the official SurgWound test split appear in every figure, chosen by the fixed rule in `../figure_set.json`: 111.jpg, 943.jpg, 3.jpg, 90.jpg, 899.jpg, 282.jpg, 937.jpg, 451.jpg, 788.jpg, 714.jpg, 686.jpg, 674.jpg.

Files:
- `convnext_tiny_384_gradcam_{1,2}.png`: Phase 2 model, original images.
- `convnext_tiny_384_inpainted_gradcam_{1,2}.png`: Phase 3 mitigated model, overlays inpainted.

## How to read the maps

Grad-CAM maps highlight the wound region the model relies on for the critical class of each head (erythema present, edema present, purulent exudate, elevated infection risk). At 12x12 resolution (32 px cells) they do not identify specific features such as a suture line or a rim of redness, and they are not a clinical finding.

## Identifiability review

All 12 source images were reviewed at full resolution before publishing:
- **No faces, names, tattoos or jewelry** are visible in any of the 12.
- **451.jpg** carried a platform watermark with an account number. It is pixelated in every figure (and inpainted in the mitigated-model input).
- **111.jpg, 937.jpg, 943.jpg** carry clinical captions (procedure name, post-operative day). They are pixelated for display, since caption text could help locate the original post.
- **788.jpg** shows phone notification and editing UI with no personal information; its text is pixelated as well.
- Small platform corner logos (not a personal identifier) remain on several images.
