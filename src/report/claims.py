"""Rule-based claim extraction from wound reports.

A claim is (attribute, value) asserted about the wound. The extractor is
deliberately simple and transparent so its errors can be inspected, and it is
validated against the SurgWound expert reports and labels before use
(scripts/phase5_reports.py).

Rules:
- Text is split into sentences, then into clauses at contrast words
  ("but", "however", "though", "while", "although", "whereas", ";").
- Advice and hypothetical text is skipped ("monitor for signs of infection
  such as redness or swelling", "to reduce edema"): a term is skipped if an
  advice cue precedes it in the clause or sits in its comma segment, so "risk
  is low, with a recommendation for routine care" still yields the risk claim.
- A finding term is negated when a negation cue precedes it in the same
  clause with no positive marker in between ("no signs of erythema, edema,
  or exudate" negates all three; "no exudate, with existing erythema" does
  not negate erythema), or when a negation follows it ("erythema is absent",
  "erythema and edema are non-existent").
- A finding stated as uncertain ("uncertain edema status", "erythema remains
  uncertain") yields no claim: it is neither supported nor contradicted.
"""
import re
from dataclasses import dataclass

TERMS = {
    "erythema": [r"erythema\w*", r"redness", r"reddened", r"reddish", r"red(?= (?:skin|area|margin|edges?|rim|halo))",
                 r"inflamed"],
    "edema": [r"o?edema\w*", r"swelling", r"swollen", r"puffiness", r"puffy"],
    "exudate_any": [r"exudate\w*", r"drainage", r"draining", r"discharge", r"oozing", r"weeping", r"fluid"],
    "exudate_purulent": [r"(?<!non-)(?<!non)purulent", r"seropurulent", r"pus\b", r"pustul\w*", r"yellow(?:ish)? (?:discharge|drainage|exudate)"],
    "exudate_nonpurulent": [r"non-?purulent", r"serous", r"serosanguineous", r"sanguineous", r"bloody", r"blood[- ]tinged", r"bleeding",
                            r"clear fluid"],
    "infection": [r"infection", r"infected", r"cellulitis", r"abscess"],
    "healing_healed": [r"(?<!non-)(?<!non)(?<!not )(?<!un)healed\b", r"well[- ]healed", r"fully healed"],
    "healing_not": [r"non-?healed", r"not (?:yet )?healed", r"unhealed", r"open wound", r"dehisce\w*", r"wound separation"],
}

_FINDING = r"(?:erythema|redness|o?edema|swelling|exudate|drainage|discharge)"
_LIST = r"(?:(?:\s*(?:,|and|or))+\s*" + _FINDING + r")*"
_PP = r"(?:\s+(?:around|at|near|along|on|in|of|over|surrounding)\s+(?:the\s+|this\s+)?\w+(?:\s+(?:site|line|edges?|area))?)?"
_VERB = _PP + r"\s*(?:(?:is|are|was|were|remains?|appears?|seems?)\s+)?"
_FILLER = r"(?:(?:all|both|normal|and|completely|entirely)\s+)*"
_NEG_WORD = r"(?:absent|non-existent|nonexistent|not (?:present|observed|seen|evident|noted|visible)|none)\b"
NEG_BEFORE = r"\b(?:no|not|without|absence of|absent|free of|negative for|non-existent|nonexistent|lack of|lacks|denies|none)\b"
NEG_AFTER = r"^" + _LIST + r"\s*(?:status\s+|characteristics\s+)?" + _VERB + _FILLER + _NEG_WORD
_UNC = r"(?:uncertain|unclear|undetermined|indeterminate|unknown)"
UNC_BEFORE = _UNC + r"\s+(?:\w+\s+)?$"
UNC_AFTER = r"^" + _LIST + r"\s*(?:status\s+|characteristics\s+)?" + _VERB + r"(?:" + _UNC + r"|cannot be (?:determined|assessed))\b"
POSITIVE_BREAK = (r"\b(?:with|existing|existent|present|exhibit\w*|shows?|showing|has|have|displays?|notable|evident|"
                  r"mild|moderate|severe|significant)\b")
ADVICE = (r"\b(?:monitor\w*|watch\w*|prevent\w*|avoid\w*|recommend\w*|should|advis\w*|ensure|if|to reduce|"
          r"to minimi[sz]e|for (?:any |potential |possible )?(?:signs|changes|symptoms)|look out|in case|"
          r"risk of developing|educat\w*|instruct\w*|follow[- ]up|seek|encourag\w*|reduce|potential|such as|keep\w*|"
          r"maintain\w*|care instructions|promot\w*|elevat(?:e|ing) the)\b")
CONTRAST = r"\b(?:but|however|though|although|while|whereas)\b|;"

_RISK_LEVEL = r"(low|lower|minimal|medium|moderate|intermediate|high|elevated|significant)"
RISK_PATTERNS = [
    r"infection risk(?: assessment| level)?(?: is| was| remains| of| appears| seems| looks)?(?: to be)?(?: deemed| assessed as| considered| rated|"
    r" categorized as| classified as)?\s+" + _RISK_LEVEL + r"\b",
    r"risk of infection(?: is| was| remains)?(?: deemed| assessed as| considered| rated)?\s+" + _RISK_LEVEL + r"\b",
    r"\b" + _RISK_LEVEL + r"(?:[- ]risk)?(?: of infection| infection risk| risk of infection)\b",
]
LEVEL_MAP = {"low": "low", "lower": "low", "minimal": "low", "medium": "medium", "moderate": "medium",
             "intermediate": "medium", "high": "high", "elevated": "elevated", "significant": "elevated"}
SIGNS = r"\b(?:signs?|evidence|suggestive|consistent with|indicat\w*|infected|cellulitis|abscess)\b"


@dataclass
class Claim:
    attribute: str   # erythema | edema | exudate | infection | infection_level | healing
    value: str       # present/absent ; none/non_purulent/purulent ; low/elevated ; low/medium/high ; healed/not_healed
    text: str        # the clause the claim came from

    def key(self):
        return (self.attribute, self.value)


def _clauses(text: str) -> list[str]:
    out = []
    for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
        out += [c.strip() for c in re.split(CONTRAST, sent, flags=re.I) if c and c.strip()]
    return out


def _find(patterns, clause):
    return [m for p in patterns for m in re.finditer(rf"\b{p}", clause, flags=re.I)]


def _in_advice(clause: str, m: re.Match) -> bool:
    """True if an advice cue occurs earlier in the clause, or anywhere in the comma
    segment holding the match ("risk is low, with a recommendation" keeps the risk)."""
    if re.search(ADVICE, clause[:m.start()], flags=re.I):
        return True
    start = clause.rfind(",", 0, m.start()) + 1
    end = clause.find(",", m.end())
    seg = clause[start:end if end >= 0 else len(clause)]
    return bool(re.search(ADVICE, seg, flags=re.I))


def _polarity(clause: str, m: re.Match) -> str | None:
    """'present', 'absent' or None (uncertain, no claim) for the term matched by m."""
    before, after = clause[:m.start()], clause[m.end():]
    if re.search(UNC_BEFORE, before, flags=re.I) or re.search(UNC_AFTER, after, flags=re.I):
        return None
    if re.search(NEG_AFTER, after, flags=re.I):
        return "absent"
    cues = list(re.finditer(NEG_BEFORE, before, flags=re.I))
    if cues and not re.search(POSITIVE_BREAK, before[cues[-1].end():], flags=re.I):
        return "absent"
    return "present"


def _matches(key, cl):
    return [(m, _polarity(cl, m)) for m in _find(TERMS[key], cl) if not _in_advice(cl, m)]


def extract_claims(text: str) -> list[Claim]:
    claims: list[Claim] = []
    for cl in _clauses(text):
        low = cl.lower()
        for attr in ("erythema", "edema"):
            for _, pol in _matches(attr, cl):
                if pol:
                    claims.append(Claim(attr, pol, cl))
        pur, non, gen = _matches("exudate_purulent", cl), _matches("exudate_nonpurulent", cl), _matches("exudate_any", cl)
        if any(p == "present" for _, p in pur):
            claims.append(Claim("exudate", "purulent", cl))
        elif any(p == "present" for _, p in non):
            claims.append(Claim("exudate", "non_purulent", cl))
        elif any(p == "absent" for _, p in gen + pur + non):
            claims.append(Claim("exudate", "none", cl))
        level = None
        for pat in RISK_PATTERNS:
            mm = re.search(pat, low)
            if mm and not _in_advice(cl, mm):
                level = LEVEL_MAP[mm.group(1)]
                break
        if level:
            claims.append(Claim("infection", "low" if level == "low" else "elevated", cl))
            if level in ("low", "medium", "high"):  # "elevated" names no specific level
                claims.append(Claim("infection_level", level, cl))
        else:
            for _, pol in _matches("infection", cl):
                if pol == "absent":
                    claims.append(Claim("infection", "low", cl))
                elif pol == "present" and re.search(SIGNS, low):
                    claims.append(Claim("infection", "elevated", cl))
        for v, key in (("not_healed", "healing_not"), ("healed", "healing_healed")):
            if _matches(key, cl):
                claims.append(Claim("healing", v, cl))
                break
    seen, out = set(), []
    for c in claims:
        if c.key() not in seen:
            seen.add(c.key())
            out.append(c)
    return out


def claims_by_attribute(claims: list[Claim]) -> dict[str, set[str]]:
    d: dict[str, set[str]] = {}
    for c in claims:
        d.setdefault(c.attribute, set()).add(c.value)
    return d
