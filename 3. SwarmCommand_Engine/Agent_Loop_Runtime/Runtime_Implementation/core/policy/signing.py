"""HMAC-SHA256 signing primitives for sandbox-issued policy updates.

Signing keeps one job: produce a deterministic, verifiable `signature_id`
string that the promotion pipeline can recompute and compare in constant
time. The dev key is in-process for now; a real key escrow can replace
``default_signing_key`` later without changing call sites.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from typing import Any

SIGNATURE_PREFIX = "hmac_sha256:"
_DEFAULT_DEV_SECRET = (
    b"northstar-swarmcommand-dev-policy-signing-key-v1-do-not-use-in-production"
)


@dataclass(frozen=True)
class SigningKey:
    """Opaque holder for the secret bytes used by HMAC-SHA256.

    Frozen so a key cannot be silently rotated on a long-lived config object.
    """

    secret: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.secret, (bytes, bytearray)) or len(self.secret) < 16:
            raise ValueError("signing key secret must be at least 16 bytes")


def default_signing_key() -> SigningKey:
    """Return the development signing key (env-overridable).

    Reads ``NORTHSTAR_POLICY_SIGNING_KEY`` if set; otherwise returns the
    deterministic in-process dev key so tests and local runs are reproducible.
    """

    env_secret = os.environ.get("NORTHSTAR_POLICY_SIGNING_KEY")
    if env_secret:
        return SigningKey(secret=env_secret.encode("utf-8"))
    return SigningKey(secret=_DEFAULT_DEV_SECRET)


def canonical_payload(payload: dict[str, Any], signer_id: str) -> bytes:
    """Serialize ``payload`` deterministically and bind it to ``signer_id``.

    Sorted keys + no whitespace + ensure_ascii=False is enough for this
    prototype: payloads are small, structured Pydantic dumps, and never
    contain ordering-sensitive data we want to preserve.
    """

    if not signer_id:
        raise ValueError("signer_id is required")
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"{signer_id}|{body}".encode("utf-8")


def sign(payload: dict[str, Any], signer_id: str, key: SigningKey) -> str:
    """Return a signature id for ``payload`` signed by ``signer_id``."""

    digest = hmac.new(key.secret, canonical_payload(payload, signer_id), hashlib.sha256).hexdigest()
    return f"{SIGNATURE_PREFIX}{digest}"


def verify(
    payload: dict[str, Any],
    signer_id: str,
    signature_id: str,
    key: SigningKey,
) -> bool:
    """Return True if ``signature_id`` matches ``payload`` for ``signer_id``.

    Uses ``hmac.compare_digest`` for a constant-time comparison so the
    pipeline cannot be turned into a signature oracle by timing.
    """

    if not signature_id or not signature_id.startswith(SIGNATURE_PREFIX):
        return False
    expected = sign(payload, signer_id, key)
    return hmac.compare_digest(expected, signature_id)
