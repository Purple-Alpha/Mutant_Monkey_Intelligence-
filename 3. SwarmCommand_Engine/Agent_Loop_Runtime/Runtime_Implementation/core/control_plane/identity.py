"""AgentIdentityGateway — Phase 6 (Layer 6), Gate 5: zero trust between agents.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D7 + §3.7.

Every agent action is bound to an **authenticated identity**, a **tenant scope**,
a **tool scope**, and **revocable access**. No agent trusts another by default.
A token issued to one agent, presented by a different agent, is rejected at the
gateway **regardless of payload content** (the BRC-D7 metastasis test).

This component defines the **security property** and the gateway enforcement
point. Specific protocol choices (mTLS, JWT, SPIFFE) are deferred to Phase 6+
infrastructure hardening (contract §3.7); here ``token`` / ``agent_id`` /
``tenant_id`` are opaque caller-supplied labels, exactly as the Phase 1
Component-2 boundary keeps ``actor_id`` opaque.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class IdentityError(Exception):
    """Raised when an action fails identity / scope / revocation checks (fail-safe)."""


@dataclass(frozen=True)
class AgentIdentity:
    """An issued, scoped, revocable agent identity."""

    token: str
    agent_id: str
    tenant_id: str
    tool_scope: frozenset[str]


@dataclass(frozen=True)
class ResolvedIdentity:
    """Result of a successful gateway identity resolution."""

    agent_id: str
    tenant_id: str
    tool: str


@dataclass
class AgentIdentityGateway:
    """Issues, resolves, and revokes scoped agent identities (Gate 5)."""

    _by_token: dict[str, AgentIdentity] = field(default_factory=dict)
    _revoked: set[str] = field(default_factory=set)

    def issue(
        self,
        *,
        token: str,
        agent_id: str,
        tenant_id: str,
        tool_scope: frozenset[str] | set[str] | list[str],
    ) -> AgentIdentity:
        if not token or not agent_id or not tenant_id:
            raise IdentityError("identity requires token, agent_id, and tenant_id")
        identity = AgentIdentity(
            token=token,
            agent_id=agent_id,
            tenant_id=tenant_id,
            tool_scope=frozenset(tool_scope),
        )
        self._by_token[token] = identity
        return identity

    def revoke(self, token: str) -> None:
        """Revoke a token. Revocation is irreversible for this token (fail-safe)."""

        self._revoked.add(token)

    def resolve(
        self,
        *,
        token: str,
        claimed_agent_id: str,
        tenant_id: str,
        tool: str,
    ) -> ResolvedIdentity:
        """Resolve and authorize an agent action. Raises ``IdentityError`` on any
        violation — unknown token, **cross-agent token use**, tenant-scope
        mismatch, out-of-scope tool, or revoked access. No agent trusts another
        by default; the check is on the binding, never on the payload.
        """

        identity = self._by_token.get(token)
        if identity is None:
            raise IdentityError("unknown identity token")
        if token in self._revoked:
            raise IdentityError(f"identity token for {identity.agent_id!r} is revoked")
        # BRC-D7 metastasis test: a token bound to agent A presented by agent B
        # is rejected regardless of payload content.
        if identity.agent_id != claimed_agent_id:
            raise IdentityError(
                f"cross-agent token use: token bound to {identity.agent_id!r}, "
                f"presented as {claimed_agent_id!r}"
            )
        if identity.tenant_id != tenant_id:
            raise IdentityError(
                f"tenant-scope mismatch: token scoped to {identity.tenant_id!r}, "
                f"action claimed tenant {tenant_id!r}"
            )
        if tool not in identity.tool_scope:
            raise IdentityError(
                f"tool {tool!r} is outside the token's tool scope for "
                f"{identity.agent_id!r}"
            )
        return ResolvedIdentity(
            agent_id=identity.agent_id,
            tenant_id=identity.tenant_id,
            tool=tool,
        )


__all__ = [
    "IdentityError",
    "AgentIdentity",
    "ResolvedIdentity",
    "AgentIdentityGateway",
]
