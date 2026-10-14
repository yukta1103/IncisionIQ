"""Claim extraction for structured (markdown) reports, such as the VLM's.

The prose extractor in claims.py was built and validated on SurgWound's expert
reports, which are short paragraphs. The VLM writes long markdown reports with
one section per requested aspect, tables, and lists of warning signs ("seek
care if: purulent discharge, spreading redness"). Run over the whole document,
the prose extractor reads headings and warning-sign lists as findings.

This module reads each attribute only from its own section, only up to the
first escalation or advice list, and ignores headings, tables and
recommendation sections. A small lexicon handles short leading verdicts
("**Present: likely mild.**", "**Minimal.**", "Risk level: Moderate").
It is validated against hand labels (scripts/phase5_markdown_validation.py).
"""
import re

from src.report.claims import ADVICE, Claim, extract_claims

SECTION_ATTR = [  # first match wins, order matters
    (r"infection\s+risk", "infection"),
    (r"erythema|redness", "erythema"),
    (r"o?edema|swelling", "edema"),
    (r"exudate|drainage", "exudate"),
    (r"wound\s+status|healing", "healing"),
]
STOP_LINE = (r"\b(?:escalat\w*|seek|if any|if you|red flags?|warning signs?|signs to (?:watch|monitor)|"
             r"watch for|would (?:suggest|indicate)|could indicate|concern for|consider)\b")
ABSENT_LEAD = r"^(?:none|no\b|absent|not (?:present|evident|apparent|visible|seen|observed|identified)|non-existent|nil)"
PRESENT_LEAD = (r"^(?:present|yes\b|mild|moderate|severe|marked|minimal|slight|significant|extensive|localized|"
                r"diffuse|trace|small amount|faint)")
RISK_LEAD = r"(?:risk(?: level)?\s*[:\-]?\s*)?(low|minimal|moderate|medium|intermediate|high|elevated|significant)\b"
RISK_MAP = {"low": "low", "minimal": "low", "moderate": "medium", "medium": "medium", "intermediate": "medium",
            "high": "high", "elevated": "elevated", "significant": "elevated"}
HEALED_CUES = r"\b(?:re-?epitheliali[sz]ed|fully healed|well-healed|healed\b|mature scar|scar\b|remodel\w*|maturation)"
NOT_HEALED_STRONG = r"\b(?:open (?:wound|area)s? (?:is|are) (?:present|visible)|granulat\w*|defect|dehisced|slough|ulcer\w*|necro\w*)"
NOT_HEALED_CUES = (r"\b(?:early (?:proliferative|healing|inflammatory)|inflammatory phase|proliferative phase|crust\w*|"
                   r"scab\w*|eschar|fresh|recent(?:ly)? (?:placed|closed)|sutures? (?:are )?(?:still )?in place)")


def _clean(line: str) -> str:
    line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)        # bullets and numbering
    line = re.sub(r"[*_`]+", "", line)                           # emphasis
    line = line.replace("/", " or ").strip()
    return line


def sections(text: str) -> list[tuple[str, list[str]]]:
    out, head, body = [], "", []
    for raw in text.splitlines():
        h = re.match(r"^\s*#{1,6}\s*(.+?)\s*$", raw)
        if h:
            out.append((head, body))
            head, body = h.group(1), []
        else:
            body.append(raw)
    out.append((head, body))
    return out


def section_attribute(heading: str) -> str | None:
    h = re.sub(r"^\d+[.)]\s*", "", heading.strip().strip("*")).lower()
    if re.search(r"recommend|seek|red flag|warning|monitor|plan|management|care\b|follow|instruction|differential|"
                 r"summary|impression|disclaimer|limitation|cause", h):
        return None
    for pat, attr in SECTION_ATTR:
        if re.search(pat, h):
            return attr
    return None


def section_lines(body: list[str]) -> list[str]:
    """Statement lines of a section, up to the first escalation or advice list; tables dropped."""
    lines = []
    for raw in body:
        if not raw.strip() or raw.strip().startswith("|") or re.match(r"^\s*-{3,}\s*$", raw):
            continue
        line = _clean(raw)
        if re.search(STOP_LINE, line, flags=re.I):
            break
        if line.endswith(":") and re.search(ADVICE, line, flags=re.I):
            break
        lines.append(line if line.endswith((".", "!", "?")) else line + ".")
    return lines


def _lead_verdict(attr: str, line: str) -> str | None:
    """Short verdict at the start of a section, after an optional 'Presence:'-style key."""
    body = re.sub(r"^[^:]{0,40}:\s*", "", line.lower()) if ":" in line[:42] else line.lower()
    if re.search(ABSENT_LEAD, body):
        return "absent"
    if re.search(PRESENT_LEAD, body):
        return "present"
    vals = {c.value for c in extract_claims(line) if c.attribute == attr}
    return vals.pop() if len(vals) == 1 else None


def _section_claims(attr: str, lines: list[str]) -> list[Claim]:
    """One resolved claim per attribute (plus the risk level for infection)."""
    text = " ".join(lines)
    found = [c for c in extract_claims(text) if c.attribute == attr]
    if attr == "infection":
        m = re.search(RISK_LEAD, lines[0].lower())
        if m:
            lvl = RISK_MAP[m.group(1)]
            out = [Claim("infection", "low" if lvl == "low" else "elevated", lines[0])]
            return out + ([Claim("infection_level", lvl, lines[0])] if lvl in ("low", "medium", "high") else [])
        levels = [c for c in extract_claims(text) if c.attribute in ("infection", "infection_level")]
        return levels[:2]
    if attr in ("erythema", "edema"):
        v = _lead_verdict(attr, lines[0])          # the section's opening statement decides
        if v is None:
            vals = {c.value for c in found}
            v = vals.pop() if len(vals) == 1 else ("present" if vals else None)
        return [Claim(attr, v, lines[0])] if v else []
    if attr == "exudate":
        vals = {c.value for c in found}
        for v in ("purulent", "non_purulent", "none"):  # a named drainage type beats "amount: none to minimal"
            if v in vals:
                return [Claim("exudate", v, text[:200])]
        return [Claim("exudate", "none", lines[0])] if re.search(ABSENT_LEAD + r"|amount\W+none", lines[0].lower()) else []
    if attr == "healing":
        if re.search(NOT_HEALED_STRONG, text, flags=re.I):
            return [Claim("healing", "not_healed", text[:200])]
        if re.search(HEALED_CUES, text, flags=re.I):
            return [Claim("healing", "healed", text[:200])]
        if re.search(NOT_HEALED_CUES, text, flags=re.I):
            return [Claim("healing", "not_healed", text[:200])]
        vals = {c.value for c in found}
        return [Claim("healing", vals.pop(), lines[0])] if len(vals) == 1 else []
    return []


def extract_markdown_claims(text: str) -> list[Claim]:
    claims: list[Claim] = []
    for heading, body in sections(text):
        attr = section_attribute(heading)
        if attr is None:
            continue
        lines = section_lines(body)
        if not lines:
            continue
        claims += _section_claims(attr, lines)
    seen, out = set(), []
    for c in claims:
        if c.key() not in seen:
            seen.add(c.key())
            out.append(c)
    return out
