"""Three-level verdict from image attributes and patient answers.

Explicit rules, checked in this order. The image enters only through the
infection band (Phase 4 flag-or-refer operating point), so a low-confidence
image can push the verdict up (uncertain band -> Watch) but never down to
On track. Drainage comes from the patient's answer, not the image (Phase 2:
the image model catches 3 of 30 purulent wounds). Fever or worsening pain
override a low-concern image band (Phase 4: 2 of 12 High-risk images fall in
that band).

Review recommended   contact the patient today
Watch                review the photo; ask for a new photo and answers in 24 to 48 hours
On track             routine follow-up per the discharge plan

All verdict, reason and action text is written for the clinician, about the patient.
"""
from dataclasses import dataclass, field

REVIEW, WATCH, ON_TRACK = "Review recommended", "Watch", "On track"
PAIN_SEVERE, PAIN_MODERATE = 7, 4


@dataclass
class PatientAnswers:
    pain: int                 # 0 to 10
    pain_worsening: bool
    fever: bool
    drainage: bool


@dataclass
class PhotoQuality:
    ok: bool = True
    reasons: list = field(default_factory=list)


def photo_quality(width: int, height: int, inpainted_area_frac: float) -> PhotoQuality:
    reasons = []
    if min(width, height) < 300:
        reasons.append("The photo is small (short side under 300 px), so wound details may not be visible.")
    if inpainted_area_frac > 0.15:
        reasons.append("More than 15% of the photo was covered by text or stickers and was removed before analysis.")
    return PhotoQuality(ok=not reasons, reasons=reasons)


def verdict(attrs: dict, answers: PatientAnswers, quality: PhotoQuality | None = None) -> dict:
    band = attrs["infection"]["band"]
    rate = round(100 * attrs["infection"]["observed_rate"])
    review, watch = [], []

    if answers.fever:
        review.append("Patient reported fever, a possible sign of surgical site infection.")
    if answers.pain_worsening:
        review.append("Patient reported that wound pain is getting worse.")
    if answers.pain >= PAIN_SEVERE:
        review.append(f"Patient rated wound pain {answers.pain} out of 10 (severe).")
    if band == "high concern":
        review.append(f"Photo is in the high-concern infection risk group (in validation, about {rate} in 100 photos "
                      "in this group were rated Medium or High risk by surgeons).")
    if answers.drainage and band != "low concern":
        review.append("Patient reported drainage, and the photo is not in the low-concern group.")

    if band == "uncertain":
        watch.append(f"Photo is in the uncertain infection risk group (in validation, about {rate} in 100 photos in "
                     "this group were rated Medium or High risk by surgeons); clinician review of the photo is needed.")
    if answers.drainage:
        watch.append("Patient reported drainage from the wound.")
    if PAIN_MODERATE <= answers.pain < PAIN_SEVERE:
        watch.append(f"Patient rated wound pain {answers.pain} out of 10 (moderate).")
    if quality is not None and not quality.ok:
        watch.extend(quality.reasons + ["The photo assessment is therefore less reliable."])

    if review:
        return {"level": REVIEW, "reasons": review + watch, "action": "Recommend contacting the patient today."}
    if watch:
        return {"level": WATCH, "reasons": watch,
                "action": "Review the photo. Recommend asking the patient for a new photo and answers in 24 to 48 hours."}
    return {"level": ON_TRACK,
            "reasons": [f"Photo is in the low-concern infection risk group (in validation, about {rate} in 100 photos in "
                        "this group were rated Medium or High risk by surgeons). Patient reported no fever, no "
                        "drainage, and mild pain (0 to 3 out of 10) that is not getting worse."],
            "action": "No action beyond routine follow-up per the discharge plan."}
