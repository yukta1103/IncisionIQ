# Example images

Four images from the official test split of the **SurgWound** dataset:

> Xu, J., Yin, C., Chatzipanagiotou, O. P., Tsilimigras, D. I., Clear, K., Yao, B., Cao, W., Wang, D., Pawlik, T. M., and Zhang, P. *SurgWound-Bench: a benchmark for surgical wound diagnosis.* npj Digital Medicine (2026). doi:10.1038/s41746-026-02791-3

Hugging Face `xuxuxuxuxu/SurgWound`, licensed under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/). The files are unmodified copies of the dataset images (714.jpg, 315.jpg, 111.jpg, 282.jpg) and are shared under the same license.

Chosen to cover the three infection-risk groups out-of-fold: 714 low concern, 315 uncertain, 111 and 282 high concern. 111.jpg carries an on-image caption (procedure name and post-operative day, no personal identifier) so the demo shows the OCR and inpainting step; the caption is removed before the model sees the photo. None of the four shows a face, name, tattoo or account number. No file has EXIF metadata.

In the demo each example is scored by the cross-validation fold model that never trained on it.
