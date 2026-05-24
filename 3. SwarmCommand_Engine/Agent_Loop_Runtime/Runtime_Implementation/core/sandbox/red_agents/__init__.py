"""Phase 1.3 Sandbox Training Pit — fraud-specialized Red profiles.

Four sandbox-only generators landed against Matt's 2026-05-21 §11
lockdown. Each generator returns a deterministic list of
``SyntheticEmailAttackCasePayload`` instances; the Red battery cycle
(``core.sandbox.red_battery``) is the single caller in normal use.

See ``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md``.
"""

from __future__ import annotations

from typing import Callable

from core.blackboard import SyntheticEmailAttackCasePayload

from . import (
    bucket_e_probes,
    fake_invoice_red,
    malicious_attachment_red,
    obfuscated_url_red,
    vendor_update_red,
)

CaseGenerator = Callable[..., list[SyntheticEmailAttackCasePayload]]

# Authoritative ordering used by the Red battery cycle.
RED_PROFILE_MODULES = (
    fake_invoice_red,
    vendor_update_red,
    malicious_attachment_red,
    obfuscated_url_red,
)

__all__ = [
    "CaseGenerator",
    "RED_PROFILE_MODULES",
    "bucket_e_probes",
    "fake_invoice_red",
    "malicious_attachment_red",
    "obfuscated_url_red",
    "vendor_update_red",
]
