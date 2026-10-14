# Example images

Four images from the official test split of the **SurgWound** dataset:

> Xu, J., Yin, C., Chatzipanagiotou, O. P., Tsilimigras, D. I., Clear, K., Yao, B., Cao, W., Wang, D., Pawlik, T. M., and Zhang, P. *SurgWound-Bench: a benchmark for surgical wound diagnosis.* npj Digital Medicine (2026). doi:10.1038/s41746-026-02791-3

Hugging Face `xuxuxuxuxu/SurgWound`, licensed under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/). The files are unmodified copies of the dataset images (79.jpg, 66.jpg, 268.jpg, 30.jpg) and are shared under the same license.

Chosen by a fixed rule stratified by surgeon label, blind to model performance (`select_examples` in `scripts/phase6_build_deployment.py`). From the official test split, held out by the fold 0 model the demo uses, with no OCR detection and no redaction box, the lowest-ID image meeting each condition:
- 79.jpg: surgeon-rated Low, predicted low concern;
- 66.jpg: surgeon-rated Medium (Elevated), predicted high concern;
- 268.jpg: surgeon-rated Low, predicted uncertain (the referral band);
- 30.jpg: surgeon-rated Low, predicted high concern (a false alarm).

The images were also checked by eye. None shows a caption, face, name, tattoo or account number. 268.jpg shows a child's neck and the back of the head, with no facial features, and 79.jpg shows a clinician's white coat with no face. Small corner platform logos remain, as in the training data. No file has EXIF metadata.

In the demo every photo is scored by the fold 0 model, which never trained on these four.
