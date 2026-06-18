"""Load Fission policy-as-code — immutable versioned control-plane policy (LF2-D10).

Governing contract
------------------
``4. Product_Roadmap/Load_Fission_Contract_v2.md`` — §13 SIGNED 2026-06-13
(Matt Nichol) — LF2-D10, §8 fission fallback mode.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadFissionPolicy:
    """Immutable load-fission policy version evaluated by the control plane."""

    version: str
    max_children: int
    max_depth: int = 1
    fallback_disabled: bool = False
    per_tenant_spawn_quota: int = 10
    global_spawn_quota: int = 100
    circuit_breaker_threshold: int = 5
    child_ttl_seconds: float = 300.0

    def with_fallback_disabled(self) -> LoadFissionPolicy:
        return LoadFissionPolicy(
            version=f"{self.version}+fallback_disabled",
            max_children=self.max_children,
            max_depth=self.max_depth,
            fallback_disabled=True,
            per_tenant_spawn_quota=self.per_tenant_spawn_quota,
            global_spawn_quota=self.global_spawn_quota,
            circuit_breaker_threshold=self.circuit_breaker_threshold,
            child_ttl_seconds=self.child_ttl_seconds,
        )


DEFAULT_LOAD_FISSION_POLICY = LoadFissionPolicy(version="lf2-v1.0.0", max_children=3)


class LoadFissionPolicyStore:
    """Versioned immutable policy registry — no in-place mutation (LF2-D10)."""

    def __init__(self, policies: dict[str, LoadFissionPolicy] | None = None) -> None:
        self._policies: dict[str, LoadFissionPolicy] = dict(policies or {})
        if DEFAULT_LOAD_FISSION_POLICY.version not in self._policies:
            self._policies[DEFAULT_LOAD_FISSION_POLICY.version] = DEFAULT_LOAD_FISSION_POLICY

    def get(self, version: str) -> LoadFissionPolicy:
        if version not in self._policies:
            raise KeyError(f"unknown load fission policy version: {version}")
        return self._policies[version]

    def register(self, policy: LoadFissionPolicy) -> LoadFissionPolicy:
        if policy.version in self._policies:
            raise ValueError(f"policy version already registered: {policy.version}")
        self._policies[policy.version] = policy
        return policy

    def versions(self) -> tuple[str, ...]:
        return tuple(sorted(self._policies))


__all__ = [
    "LoadFissionPolicy",
    "LoadFissionPolicyStore",
    "DEFAULT_LOAD_FISSION_POLICY",
]
