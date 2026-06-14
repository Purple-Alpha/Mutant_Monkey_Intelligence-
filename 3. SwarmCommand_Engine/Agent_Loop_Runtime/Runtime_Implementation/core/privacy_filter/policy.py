"""PolicyStore — per-tenant sharing policy resolution (stage 2, §3.2 / PF-D6).

Governing contract
------------------
``4. Product_Roadmap/Privacy_Filter_Contract.md`` — §15 SIGNED 2026-06-14
(Matt Nichol) — PF-D6 + §3.2 + §5.

Tenant-specific policy is authoritative. There is **no global permissive
default** (PF-D6): absence or ambiguity of policy resolves conservatively — do
not broadcast. Resolution raises so the pipeline fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.privacy_filter.state import BlockReason, SharingPolicy


class PolicyResolutionError(Exception):
    """Raised when a policy cannot be resolved — pipeline fails closed (PF-D6).

    Carries the conservative ``BlockReason`` so the audit record explains the
    refusal (PF-D9).
    """

    def __init__(self, reason: BlockReason, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason
        self.detail = detail


@dataclass
class PolicyStore:
    """In-process per-tenant sharing-policy registry (§5).

    No persistence technology is introduced (out of scope, deferred to the Lung
    contract); this is the resolution surface stage 2 calls.
    """

    _policies: dict[str, SharingPolicy] = field(default_factory=dict)

    def set_policy(self, policy: SharingPolicy) -> None:
        self._policies[policy.tenant_id] = policy

    def resolve(self, tenant_id: str) -> SharingPolicy:
        """Resolve the authoritative policy for ``tenant_id`` or fail closed.

        Absent policy -> POLICY_ABSENT. Present-but-incomplete policy -> treated
        as ambiguous (POLICY_AMBIGUOUS). Either way the pipeline must not
        broadcast (PF-D6).
        """

        policy = self._policies.get(tenant_id)
        if policy is None:
            raise PolicyResolutionError(
                BlockReason.POLICY_ABSENT,
                f"no sharing policy for tenant {tenant_id!r}; fail closed",
            )
        if not policy.is_complete():
            raise PolicyResolutionError(
                BlockReason.POLICY_AMBIGUOUS,
                f"sharing policy for tenant {tenant_id!r} is incomplete/ambiguous; "
                "fail closed",
            )
        return policy


__all__ = ["PolicyResolutionError", "PolicyStore"]
