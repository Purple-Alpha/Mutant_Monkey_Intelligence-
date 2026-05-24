"""NorthStar Inbox Shield — Phase 1.2 body-signal detector.

Pure-function detector for the two body-text precursor signals called out in
the 12-month roadmap Month 3 deliverables:

- Credential-harvesting language ("verify your account", "reset your password",
  "confirm your login", etc.).
- MFA-fatigue language ("approve the sign-in attempt", "code: 123456",
  "Microsoft Authenticator prompt", "we sent a verification code", etc.).

Both detectors return a 0–100 score and a tuple of ``PrecursorIndicator`` values
they justify. Pattern lists are case-insensitive and intentionally conservative
to protect the Month 2 0% legit-FPR result.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from core.blackboard import PrecursorIndicator

# Credential-reset / "verify your account" style phrases. Designed to catch
# common credential-harvesting templates without firing on routine IT
# notifications ("your password expires in 14 days" is intentionally NOT in
# this list — that's an internal-IT pattern, not a credential-harvest cue).
CREDENTIAL_RESET_PHRASES: tuple[str, ...] = (
    "reset your password",
    "reset password",
    "click here to reset",
    "click below to reset",
    "your password has been reset",
    "password expires in 24 hours",
    "password will expire today",
    "reactivate your account",
    "your account has been suspended",
    "your account will be suspended",
    "unusual sign-in activity",
    "unusual login activity",
    "suspicious sign-in",
    "click here to recover",
    "secure your account immediately",
)

# Phrases that specifically push the recipient to "verify" or "confirm" their
# credentials. Same conservatism rule applies — generic "please verify the
# meeting time" must not fire this.
ACCOUNT_VERIFICATION_PHRASES: tuple[str, ...] = (
    "verify your account",
    "verify your identity",
    "confirm your account",
    "confirm your identity",
    "confirm your credentials",
    "confirm your login",
    "update your login",
    "update your credentials",
    "validate your account",
    "validate your credentials",
)

# MFA-push / approval lures. Aimed at attacks that exploit MFA-fatigue
# (repeated push notifications until the user approves one) and at
# credential-and-code phishing.
MFA_PUSH_PHRASES: tuple[str, ...] = (
    "approve the sign-in",
    "approve the sign in",
    "approve the login",
    "approve this sign-in",
    "approve this login",
    "approve the request on your phone",
    "tap approve",
    "respond to the prompt",
    "respond to the push",
    "approve the mfa prompt",
    "approve the authenticator prompt",
    "approve the duo prompt",
    "approve the microsoft authenticator prompt",
    "sign-in request",
    "sign in request",
    "new sign-in attempt",
    "new sign in attempt",
)

# Verification-code / one-time-code lures.
VERIFICATION_CODE_PHRASES: tuple[str, ...] = (
    "verification code",
    "one-time code",
    "one-time passcode",
    "one time passcode",
    "your security code is",
    "your code is",
    "your authentication code",
    "your access code is",
    "your otp is",
    "enter the code",
    "enter this code",
    "share the code",
    "share this code",
)


@dataclass(frozen=True)
class BodySignalAssessment:
    """One sub-score's worth of body-language precursor risk.

    ``score`` is 0–100. ``indicators`` is the ``PrecursorIndicator`` tuple
    (deduplicated, source-order stable) that justify the score.
    """

    score: int
    indicators: tuple[PrecursorIndicator, ...]


def score_credential_harvesting(*texts: str | None) -> BodySignalAssessment:
    """Score credential-harvesting language across any number of body texts.

    Concatenates ``body_plain`` and any other rendered surfaces (HTML alt
    text, subject) and searches case-insensitively for the curated phrase
    lists. Emits at most two indicators:
    ``"credential_reset_language"`` and ``"account_verification_language"``.
    """

    combined = _normalise_for_matching(texts)
    indicators: list[PrecursorIndicator] = []
    score = 0

    if _any_phrase_present(combined, CREDENTIAL_RESET_PHRASES):
        indicators.append("credential_reset_language")
        score = max(score, 70)

    if _any_phrase_present(combined, ACCOUNT_VERIFICATION_PHRASES):
        indicators.append("account_verification_language")
        score = max(score, 60)

    return BodySignalAssessment(score=min(score, 100), indicators=tuple(indicators))


def score_mfa_fatigue(*texts: str | None) -> BodySignalAssessment:
    """Score MFA-fatigue / verification-code language.

    Same pure-function discipline as ``score_credential_harvesting``. Emits
    at most two indicators: ``"mfa_push_language"`` and
    ``"verification_code_language"``.
    """

    combined = _normalise_for_matching(texts)
    indicators: list[PrecursorIndicator] = []
    score = 0

    if _any_phrase_present(combined, MFA_PUSH_PHRASES):
        indicators.append("mfa_push_language")
        score = max(score, 65)

    if _any_phrase_present(combined, VERIFICATION_CODE_PHRASES):
        indicators.append("verification_code_language")
        score = max(score, 55)

    if _RE_NUMERIC_OTP.search(combined or "") is not None and score > 0:
        score = max(score, 75)

    return BodySignalAssessment(score=min(score, 100), indicators=tuple(indicators))


_RE_NUMERIC_OTP = re.compile(r"\bcode[:\s]+\d{4,8}\b", re.IGNORECASE)


def _normalise_for_matching(texts: Iterable[str | None]) -> str:
    return "\n".join(t for t in texts if t).lower()


def _any_phrase_present(haystack: str, phrases: Iterable[str]) -> bool:
    return any(phrase in haystack for phrase in phrases)
