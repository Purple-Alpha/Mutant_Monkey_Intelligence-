"""NorthStar Inbox Shield - Adversarial Prompt-Injection Detector.

Pure-function deterministic body/attachment scanner that surfaces evidence that
an inbound email is targeting the downstream LLM scoring path. The detector
never lowers a score, never calls the network, and never echoes raw matched
substrings into Blackboard or audit records.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

PromptInjectionFamily = Literal[
    "instruction_marker",
    "override_imperative",
    "role_impersonation",
    "output_control",
    "hidden_text",
]

_ZERO_WIDTH_CHARS = "\u200b\u200c\u200d\ufeff"
_HIDDEN_TEXT_KEYWORDS = (
    "wire",
    "invoice",
    "account",
    "ach",
    "aba",
    "payment",
    "system",
    "instruction",
)
_MAX_SCAN_CHARS = 200_000
_BOUNDARY_PAIR_OVERLAP_CHARS = 256

_FAMILY_PATTERNS: dict[PromptInjectionFamily, tuple[re.Pattern[str], ...]] = {
    "instruction_marker": (
        re.compile(r"\[\s*SYSTEM_INSTRUCTION\s*\]", re.IGNORECASE),
        re.compile(r"###\s*Instruction\s*:", re.IGNORECASE),
        re.compile(r"<\|im_start\|>\s*system", re.IGNORECASE),
        re.compile(r"<\|im_end\|>", re.IGNORECASE),
        re.compile(r"\bBEGIN\s+PROMPT\b", re.IGNORECASE),
        re.compile(r"\bEND\s+PROMPT\b", re.IGNORECASE),
        re.compile(r"###\s*system\b", re.IGNORECASE),
        re.compile(r"###\s*assistant\b", re.IGNORECASE),
    ),
    "override_imperative": (
        re.compile(r"\bignore\s+(?:the\s+|all\s+)?previous\s+instructions\b", re.IGNORECASE),
        re.compile(r"\bdisregard\s+(?:the\s+|all\s+)?(?:above|prior|previous)\b", re.IGNORECASE),
        re.compile(
            r"\bforget\s+(?:your\s+|all\s+)?(?:prior|previous|earlier)\s+instructions\b",
            re.IGNORECASE,
        ),
        re.compile(r"\boverride\s+(?:the\s+|your\s+)?system\s+prompt\b", re.IGNORECASE),
        re.compile(
            r"\bdo\s+not\s+follow\s+(?:the|your)\s+(?:earlier|previous)\s+instructions\b",
            re.IGNORECASE,
        ),
    ),
    "role_impersonation": (
        re.compile(r"\byou\s+are\s+now\s+(?:a|an|the)\s+", re.IGNORECASE),
        re.compile(r"\bact\s+as\s+(?:a|an|the)\s+", re.IGNORECASE),
        re.compile(r"\bpretend\s+(?:you\s+are|to\s+be)\b", re.IGNORECASE),
        re.compile(r"\brespond\s+as\s+if\s+you\s+(?:were|are)\b", re.IGNORECASE),
        re.compile(
            r"\bfrom\s+now\s+on,?\s+(?:you|act|behave|respond)\b", re.IGNORECASE
        ),
    ),
    "output_control": (
        re.compile(
            r"\bonly\s+(?:output|return|respond\s+with)\s+(?:JSON|the\s+following)\b",
            re.IGNORECASE,
        ),
        re.compile(r"\brespond\s+with\s+exactly\b", re.IGNORECASE),
        re.compile(
            r"\bdo\s+not\s+include\s+(?:any|the)\s+(?:analysis|reasoning|explanation)\b",
            re.IGNORECASE,
        ),
        re.compile(r"\bset\s+risk_score\s+to\b", re.IGNORECASE),
        re.compile(r"\bmark\s+this\s+(?:email|message)\s+as\s+safe\b", re.IGNORECASE),
        re.compile(r"\brecommend(?:ed)?_action\s*=\s*safe\b", re.IGNORECASE),
    ),
}


@dataclass(frozen=True)
class PromptInjectionAssessment:
    """One email's adversarial prompt-injection assessment."""

    score: int
    families: tuple[PromptInjectionFamily, ...]
    indicators: tuple[str, ...]


def score_prompt_injection(
    *,
    body_plain: str,
    attachments_text: Sequence[str] = (),
) -> PromptInjectionAssessment:
    """Scan body + extracted attachment text for prompt-injection evidence.

    Returns a frozen assessment with a lift-only score (0-90), the matched
    family tags, and indicator strings. Raw matched substrings are never
    returned.
    """

    raw_sources: list[str] = [(body_plain or "")[:_MAX_SCAN_CHARS]]
    raw_sources.extend(
        text[:_MAX_SCAN_CHARS] for text in attachments_text if text
    )
    normalized_sources = tuple(_normalize_for_regex(src) for src in raw_sources)
    boundary_pair_views = _build_boundary_pair_views(raw_sources)
    regex_views = normalized_sources + boundary_pair_views

    families: list[PromptInjectionFamily] = []
    for family in ("instruction_marker", "override_imperative", "role_impersonation", "output_control"):
        if _family_matches(family, regex_views):
            families.append(family)
    if _hidden_text_match(raw_sources):
        families.append("hidden_text")

    score = _score_families(families)
    indicators = tuple(f"prompt_injection:{family}" for family in families)
    return PromptInjectionAssessment(
        score=score,
        families=tuple(families),
        indicators=indicators,
    )


def _family_matches(family: PromptInjectionFamily, texts: Iterable[str]) -> bool:
    patterns = _FAMILY_PATTERNS[family]
    for text in texts:
        for pattern in patterns:
            if pattern.search(text):
                return True
    return False


def _normalize_for_regex(text: str) -> str:
    r"""Fold Unicode variants so families A-D regexes cannot be evaded by
    invisible / decorative characters inserted between tokens.

    Behavior:
      1. ``unicodedata.normalize("NFKD", text)`` decomposes compatibility
         variants AND decomposes precomposed accented characters into
         ``base + combining mark`` so the combining marks become
         standalone ``Mn`` characters and can be stripped in step 2.
         (Using NFKC instead would silently recompose the accent into a
         single ``Ll`` character and defeat the strip step below.)
      2. Combining marks (Unicode general category ``Mn``) are stripped so
         an attacker cannot hide ``ignore`` as ``i\u0301gnore`` or
         ``i\u0303gnore``.
      3. Format / zero-width characters (Unicode general category ``Cf``)
         are stripped so an attacker cannot hide ``ignore`` as
         ``i\u200bgnore`` or ``SYSTEM\u200b_INSTRUCTION`` or
         ``ignore\u00ad previous`` (soft hyphen).
      4. Any remaining whitespace character (per ``str.isspace``) is folded
         to ASCII space so ``\u00a0`` / ``\u2003`` / ``\u3000`` etc. cannot
         break ``\s+`` matches under exotic Unicode whitespace.

    The original text is preserved by the caller and passed unchanged to
    ``_hidden_text_match`` so Family E's zero-width detection continues to
    operate on raw bytes.
    """

    normalized = unicodedata.normalize("NFKD", text)
    chars: list[str] = []
    for ch in normalized:
        category = unicodedata.category(ch)
        if category == "Mn" or category == "Cf":
            continue
        if ch.isspace():
            chars.append(" ")
        else:
            chars.append(ch)
    return "".join(chars)


def _build_boundary_pair_views(raw_sources: Sequence[str]) -> tuple[str, ...]:
    r"""Build normalized scan views for every adjacent pair of sources.

    Markers and imperatives are short (<= ~50 chars). An attacker can split
    one across two attachments (``[SYSTEM`` in attachment 1, ``_INSTRUCTION]``
    in attachment 2, or ``ignore previous`` + ``instructions``) to bypass
    per-source scanning.

    For every pair ``(source_i, source_{i+1})`` this builds **two** synthetic
    views from the last ``_BOUNDARY_PAIR_OVERLAP_CHARS`` of source_i and the
    first ``_BOUNDARY_PAIR_OVERLAP_CHARS`` of source_{i+1}:

      * **No-separator view** catches mid-token splits such as
        ``[SYSTEM`` + ``_INSTRUCTION]`` where the regex token must remain
        contiguous.
      * **Single-space-separator view** catches token-boundary splits such
        as ``ignore previous`` + ``instructions`` where the regex expects
        ``\s+`` between the joined tokens.

    Each view is normalized via ``_normalize_for_regex`` so the same
    Unicode-bypass closures (D15) apply at boundaries too. The overlap
    window is bounded, so total cost is at most
    ``2 * (len(raw_sources) - 1)`` views of at most
    ``2 * _BOUNDARY_PAIR_OVERLAP_CHARS + 1`` characters each.
    """

    if len(raw_sources) < 2:
        return ()
    views: list[str] = []
    for i in range(len(raw_sources) - 1):
        left_tail = raw_sources[i][-_BOUNDARY_PAIR_OVERLAP_CHARS:]
        right_head = raw_sources[i + 1][:_BOUNDARY_PAIR_OVERLAP_CHARS]
        if not left_tail or not right_head:
            continue
        views.append(_normalize_for_regex(left_tail + right_head))
        views.append(_normalize_for_regex(left_tail + " " + right_head))
    return tuple(views)


def _hidden_text_match(texts: Iterable[str]) -> bool:
    """Detect zero-width characters placed inside or directly adjacent to a
    finance / instruction keyword.

    The detection model intentionally avoids a fixed character-radius window
    (which was bypassable by placing a zero-width character just outside the
    window). Instead, for each text source we:

    1. Strip all zero-width characters and record, for each stripped char,
       its index in the cleaned text (the position where it would have been
       inserted into the cleaned stream).
    2. Search the cleaned text for any keyword from ``_HIDDEN_TEXT_KEYWORDS``.
    3. Flag if any zero-width character index falls inside the cleaned-text
       match span ``[span_start, span_end]`` or one character outside either
       boundary (``span_start - 1`` or ``span_end + 1``).

    This catches the real attacker patterns:
      * Keyword split by a zero-width char (``wi\u200bre``).
      * Zero-width char directly before or after the keyword
        (``\u200bwire``, ``wire\u200b``).
      * Multiple zero-width chars inside a single keyword
        (``wi\u200br\u200be``).
      * A zero-width char immediately across a single whitespace boundary
        from a keyword (``wire \u200btransfer``).

    Stray zero-width characters far from any keyword (legitimate Unicode
    artifacts such as emoji zero-width joiners or BOM markers in unrelated
    text) do not trigger this family, which keeps false-positive risk low.
    """

    keywords = _HIDDEN_TEXT_KEYWORDS
    for text in texts:
        if not any(ch in text for ch in _ZERO_WIDTH_CHARS):
            continue
        cleaned_chars: list[str] = []
        zw_positions: list[int] = []
        for char in text:
            if char in _ZERO_WIDTH_CHARS:
                zw_positions.append(len(cleaned_chars))
            else:
                cleaned_chars.append(char)
        if not zw_positions:
            continue
        cleaned_lower = "".join(cleaned_chars).lower()
        for keyword in keywords:
            start = 0
            while True:
                idx = cleaned_lower.find(keyword, start)
                if idx == -1:
                    break
                span_start = idx
                span_end = idx + len(keyword)
                for zw_pos in zw_positions:
                    if span_start - 1 <= zw_pos <= span_end + 1:
                        return True
                start = idx + 1
    return False


def _score_families(families: Sequence[PromptInjectionFamily]) -> int:
    if not families:
        return 0
    marker_floor = 75 if "instruction_marker" in families else 0
    non_marker_count = sum(1 for family in families if family != "instruction_marker")
    non_marker_score = _non_marker_score(non_marker_count)
    return min(max(marker_floor, non_marker_score), 90)


def _non_marker_score(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 55
    if count == 2:
        return 70
    if count == 3:
        return 80
    return 90


__all__ = [
    "PromptInjectionAssessment",
    "PromptInjectionFamily",
    "score_prompt_injection",
]
