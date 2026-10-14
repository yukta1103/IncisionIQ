# Example images

Four images from the official test split of the **SurgWound** dataset:

> Xu, J., Yin, C., Chatzipanagiotou, O. P., Tsilimigras, D. I., Clear, K., Yao, B., Cao, W., Wang, D., Pawlik, T. M., and Zhang, P. *SurgWound-Bench: a benchmark for surgical wound diagnosis.* npj Digital Medicine (2026). doi:10.1038/s41746-026-02791-3

Hugging Face `xuxuxuxuxu/SurgWound`, licensed under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/). The files are unmodified copies of the dataset images (79.jpg, 411.jpg, 237.jpg, 521.jpg) and are shared under the same license.

Chosen by a fixed rule, not by model performance (`select_examples` in `scripts/phase6_build_deployment.py`): one image per out-of-fold infection band (79 low concern, 411 uncertain, 237 and 521 high concern), each held out by the fold 0 model the demo uses, with no OCR detection and no redaction box. All four are surgeon-rated Low risk, so 237 and 521 are high-concern false alarms. The images were also checked by eye: none shows a caption, face, name, tattoo or account number (small corner platform logos remain, as in the training data). No file has EXIF metadata.

In the demo every photo is scored by the fold 0 model, which never trained on these four.
