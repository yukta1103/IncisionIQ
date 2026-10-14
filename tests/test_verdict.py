"""Verdict rules (src/triage/verdict.py). Run: python -m pytest tests -q"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.triage.verdict import ON_TRACK, REVIEW, WATCH, PatientAnswers, photo_quality, verdict  # noqa: E402


def attrs(band):
    rate = {"low concern": 0.04, "uncertain": 0.12, "high concern": 0.29}[band]
    return {"infection": {"band": band, "observed_rate": rate}}


CALM = dict(pain=2, pain_worsening=False, fever=False, drainage=False)


@pytest.mark.parametrize("band,answers,expected", [
    ("low concern", CALM, ON_TRACK),
    ("uncertain", CALM, WATCH),                                   # low confidence never yields On track
    ("high concern", CALM, REVIEW),
    ("low concern", {**CALM, "fever": True}, REVIEW),             # fever overrides a low-concern band
    ("low concern", {**CALM, "pain_worsening": True}, REVIEW),    # worsening pain overrides a low-concern band
    ("low concern", {**CALM, "pain": 8}, REVIEW),
    ("low concern", {**CALM, "pain": 5}, WATCH),
    ("low concern", {**CALM, "drainage": True}, WATCH),           # drainage from the patient's answer
    ("uncertain", {**CALM, "drainage": True}, REVIEW),
    ("high concern", {**CALM, "drainage": True}, REVIEW),
])
def test_rules(band, answers, expected):
    v = verdict(attrs(band), PatientAnswers(**answers))
    assert v["level"] == expected
    assert v["reasons"] and all(isinstance(r, str) and r for r in v["reasons"])


def test_poor_photo_never_on_track():
    q = photo_quality(200, 180, 0.0)
    assert not q.ok
    assert verdict(attrs("low concern"), PatientAnswers(**CALM), q)["level"] == WATCH


def test_large_overlay_removed_is_flagged():
    assert not photo_quality(1000, 1000, 0.2).ok
    assert photo_quality(1000, 1000, 0.05).ok


def test_reasons_cite_band_rate():
    v = verdict(attrs("high concern"), PatientAnswers(**CALM))
    assert any("29 in 100" in r for r in v["reasons"])
