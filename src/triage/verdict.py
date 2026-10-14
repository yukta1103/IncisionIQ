"""Three-level verdict from image attributes and patient answers.

Explicit rules, checked in this order. The image enters only through the
infection band (Phase 4 flag-or-refer operating point), so a low-confidence
image can push the verdict up (uncertain band -> Watch) but never down to
On track. Drainage comes from the patient's answer, not the image (Phase 2:
the image model catches 3 of 30 purulent wounds). Fever or worsening pain
override a low-concern image band (Phase 4: 2 of 12 High-risk images fall in
that band).

Review recommended   contact the care team today
Watch                the care team reviews the photo; recheck within 24 to 48 hours
On track             routine care; keep following the discharge instructions
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
        reasons.append("The photo is small, so details of the wound may not be visible.")
    if inpainted_area_frac > 0.15:
        reasons.append("A large part of the photo was covered by text or stickers and had to be removed before analysis.")
    return PhotoQuality(ok=not reasons, reasons=reasons)


def verdict(attrs: dict, answers: PatientAnswers, quality: PhotoQuality | None = None) -> dict:
    band = attrs["infection"]["band"]
    rate = round(100 * attrs["infection"]["observed_rate"])
    review, watch = [], []

    if answers.fever:
        review.append("You reported a fever. Fever after surgery can be a sign of infection and should be checked today.")
    if answers.pain_worsening:
        review.append("You said your pain is getting worse. Pain that increases after surgery should be checked today.")
    if answers.pain >= PAIN_SEVERE:
        review.append(f"You rated your pain {answers.pain} out of 10, which is severe.")
    if band == "high concern":
        review.append(f"The photo looks similar to wounds that surgeons rated as higher infection risk "
                      f"(about {rate} in 100 photos like this were rated Medium or High).")
    if answers.drainage and band != "low concern":
        review.append("You reported drainage, and the photo is not in the low-concern group.")

    if band == "uncertain":
        watch.append(f"The photo could not be placed confidently (about {rate} in 100 photos like this were rated "
                     "Medium or High by surgeons), so the care team should look at it.")
    if answers.drainage:
        watch.append("You reported drainage from the wound. The care team should know about it.")
    if PAIN_MODERATE <= answers.pain < PAIN_SEVERE:
        watch.append(f"You rated your pain {answers.pain} out of 10, which is moderate.")
    if quality is not None and not quality.ok:
        watch.extend(quality.reasons + ["Because of this, the photo assessment is less reliable."])

    if review:
        return {"level": REVIEW, "reasons": review + watch, "action": "Contact your care team today."}
    if watch:
        return {"level": WATCH, "reasons": watch,
                "action": "Your care team will review the photo. Take a new photo and answer again in 24 to 48 hours."}
    return {"level": ON_TRACK,
            "reasons": [f"The photo is in the low-concern group (about {rate} in 100 photos like this were rated Medium "
                        "or High by surgeons), and you reported no fever, no drainage, and mild pain that is not "
                        "getting worse."],
            "action": "Keep following your discharge instructions. Contact your care team if anything changes."}
