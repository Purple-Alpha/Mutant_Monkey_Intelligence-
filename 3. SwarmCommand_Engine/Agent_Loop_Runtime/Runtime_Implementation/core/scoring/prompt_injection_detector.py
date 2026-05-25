"""NorthStar Inbox Shield - Adversarial Prompt-Injection Detector.

Pure-function deterministic body/attachment scanner that surfaces evidence that
an inbound email is targeting the downstream LLM scoring path. The detector
never lowers a score, never calls the network, and never echoes raw matched
substrings into Blackboard or audit records.
"""

from __future__ import annotations

import re
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

    text_sources: list[str] = [(body_plain or "")[:_MAX_SCAN_CHARS]]
    text_sources.extend(
        text[:_MAX_SCAN_CHARS] for text in attachments_text if text
    )
    families: list[PromptInjectionFamily] = []

    for family in ("instruction_marker", "override_imperative", "role_impersonation", "output_control"):
        if _family_matches(family, text_sources):
            families.append(family)
    if _hidden_text_match(text_sources):
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


def _hidden_text_match(texts: Iterable[str]) -> bool:
    radius = 12
    keywords = _HIDDEN_TEXT_KEYWORDS
    for text in texts:
        if not any(ch in text for ch in _ZERO_WIDTH_CHARS):
            continue
        lowered = text.lower()
        for index, char in enumerate(text):
            if char not in _ZERO_WIDTH_CHARS:
                continue
            window = lowered[max(0, index - radius) : index + radius + 1]
            cleaned = window
            for zw in _ZERO_WIDTH_CHARS:
                cleaned = cleaned.replace(zw, "")
            if any(keyword in cleaned for keyword in keywords):
                return True
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
