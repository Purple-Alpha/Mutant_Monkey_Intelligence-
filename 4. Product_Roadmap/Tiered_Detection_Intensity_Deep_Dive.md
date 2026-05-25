# Tiered Detection Intensity (Low / Medium / High) — Implementation Spec (Deep Dive)

**Status:** §11 SIGNED 2026-05-24 by Matt; implementation landed 2026-05-24; runtime verification 658 passed, 1 skipped; independent Grok audit approved.
**Authors:** Matt (operator decisions) + AI scribe (capture).
**Last reviewed:** 2026-05-24 UTC.
**Source-of-truth links:** `think_sheet.md` (Tiered Detection Intensity promote row, 2026-05-24 stress test), `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md`, `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`, `PROJECT_GUARDRAILS.md` (Guardrails 11 + 12), `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py` (overlay integration point).

This document is the specification contract for the Tiered Detection Intensity policy system. No implementation lands until the §11 Lockdown Signature is filled in by the operator. Once signed, every implementation receipt must cite this file by section number.

---

## §0 Purpose

Tiered Detection Intensity gives each tenant (typically each MSP-managed SMB) a controllable security posture — **Low**, **Medium**, or **High** — that decides which deterministic detectors run on routine mail and how much LLM-side scrutiny is applied. The policy must satisfy three simultaneous requirements:

1. **Cost / latency control.** Low-exposure tenants should not pay High-tier deliberation cost on every newsletter and transactional email.
2. **Safety floor.** Risky mail must always escalate to High scrutiny regardless of the tenant's default tier. Tier is a floor for routine mail; it is not a ceiling for risky mail.
3. **Sales formation alignment.** Essentials / Plus / Enterprise packaging maps cleanly to Low / Medium / High defaults so MSPs can sell intensity the way they already sell service tiers (Option C in `think_sheet.md` 2026-05-24).

This is the first product-policy system that ties technical cost control, tenant-scoped operator state, and commercial packaging together. It is not a new detector; it is a routing and gating policy that decides which detectors run and at what depth, while preserving every existing detector's behaviour when invoked.

---

## §1 Scope

### In scope (v1)

- Three-tier closed enum: `LOW`, `MEDIUM`, `HIGH`.
- Tenant-scoped operator-controlled state stored alongside the existing kill switch surface (`core/operator_state/`), per Guardrail 12 separation.
- Closed `DetectorIdentity` enum covering the five currently implemented detector slots in `core/scoring/email_risk_scoring_agent.py`:
  - LLM primary scoring pass
  - Ransomware-precursor / attachment / URL overlay
  - Header divergence detector
  - Ghost-thread detector
  - Financial State Ledger / Delta Tripwire
- Per-detector minimum-tier metadata. Detectors below or equal to the effective tier run; detectors above the effective tier are skipped.
- Closed `ForcedEscalationTrigger` enum. Triggers are derived from always-on detector evidence and can lift a single email's effective tier to `HIGH` regardless of the tenant default.
- Pure resolver function returning a `ProfileResolution` for a given (tenant_default, forced_triggers) input.
- Add-on detector enable list per tenant (lift-only — add-ons can enable a detector above the tier minimum but cannot disable a detector that the effective tier would otherwise enable).
- Sales-plan → default-profile mapping locked: Essentials = LOW, Plus = MEDIUM, Enterprise = HIGH.
- Audit-row emission on every tenant profile change AND on every forced-escalation event.
- Daily-digest and email-analysis output surfaces extended to expose `effective_profile` and any `forced_escalation_triggers`.
- Gate tests proving every §2 locked decision, every closed enum's exhaustiveness, the lift-only invariant, and the cost-monotonicity invariant (call count Low ≤ Medium ≤ High when no escalation fires).

### Out of scope (v1)

- High-only deliberation primitives (multi-agent debate, judge pass, devil's-advocate pass, skeptic pass on clean mail, visible reasoning trace surface). These are listed as `HIGH`-tier in the registry but no `HIGH`-only detector ships in v1. `HIGH` in v1 = `MEDIUM` detector set, fully enabled, with future deliberation primitives reserved.
- PDF metadata fingerprinting, micro-temporal vendor-send-window baselining, callback / TOAD scan, structural payload OCR. Each requires its own §11-signed spec before being added to the `DetectorIdentity` enum.
- Self-service MSP UI for switching tenant tiers. v1 surface is operator-only writes (CLI / REPL / future operator dashboard), matching the kill-switch convention.
- Per-rule sensitivity dialing inside a detector. v1 is detector-on / detector-off; thresholds remain detector-internal.
- Cross-tenant reputation or rule sharing between profiles.
- Automatic profile downgrade after a quiet period. The tier can only be changed by an explicit operator-written audit-logged write.
- Pricing engine, invoice generation, or sales-CRM integration. The sales-plan mapping is documentation + a single locked lookup; commercial systems are outside the runtime.

---

## §2 Locked Architectural Decisions

| # | Decision | Locked Value | Rationale |
|---|---|---|---|
| D1 | Runtime location for pure types + resolver | `core/operator_state/security_profile.py` | Tier is operator-controlled tenant policy. Lives next to the kill switch surface (Guardrail 12) and is read by agents the same way `is_kill_switch_engaged` is. No new package required. |
| D2 | Storage location for per-tenant state | `blackboard_root/operator_state/security_profiles/<tenant_id>.json` (one file per tenant) | Matches Vendor Baseline Store's per-tenant directory pattern. Cross-tenant reads are impossible by construction. |
| D3 | Closed tier enum | `SecurityProfile = Literal["low", "medium", "high"]` | Three tiers exactly. Future tiers require a spec revision. |
| D4 | Default tier when no state file exists | `MEDIUM` | Locked decision from `think_sheet.md` 2026-05-24. A tenant with no profile written behaves as the standard SMB posture, not as Low. |
| D5 | Tier ordering | `LOW < MEDIUM < HIGH` (integer ranks 0 / 1 / 2 used internally) | Required by min-tier comparisons and lift-only invariant. |
| D6 | Closed `DetectorIdentity` enum (v1) | `LLM_PRIMARY`, `RANSOMWARE_PRECURSOR_OVERLAY`, `HEADER_DIVERGENCE`, `GHOST_THREAD`, `FINANCIAL_STATE_LEDGER` | Matches exactly the five detector slots already wired into `_overlay_ransomware_precursor`. v2 detectors will extend this enum in their own §11-signed specs. |
| D7 | Always-on (LOW-tier) detector set | `LLM_PRIMARY`, `RANSOMWARE_PRECURSOR_OVERLAY`, `HEADER_DIVERGENCE`, `GHOST_THREAD` | Cheap deterministic + the single LLM pass. Required so forced-escalation triggers always have evidence to fire on, even at Low. |
| D8 | MEDIUM-tier detectors (v1) | `FINANCIAL_STATE_LEDGER` | The only MEDIUM-only detector implemented today. PDF metadata / micro-temporal / callback-TOAD are v2 deferrals. |
| D9 | HIGH-only detectors (v1) | None implemented; reserved for v2 deliberation work | Locked so v1 callers cannot accidentally introduce a HIGH-only path before a spec defines it. |
| D10 | Closed `ForcedEscalationTrigger` enum (v1) | `LLM_HIGH_RISK_SCORE`, `HEADER_DIVERGENCE_STRONG`, `GHOST_THREAD_DETECTED`, `MANUAL_OPERATOR_ESCALATION` | Each trigger is detectable from the always-on detector set or from operator input. Triggers that depend on tier-gated detectors are explicit v2 deferrals (see §6 + §10). |
| D11 | Lift-only invariant | Forced escalation always raises the effective tier; it never lowers. Add-on detectors can only enable, never disable. | Guarantees a tenant on Low cannot be silently downgraded to ignore a risky email. Matches the lift-only invariant already in `_overlay_ransomware_precursor`. |
| D12 | Sales-plan → default-profile mapping | `Essentials → LOW`, `Plus → MEDIUM`, `Enterprise → HIGH` (Option C) | Locked from `think_sheet.md` 2026-05-24. Captured as a constant lookup; commercial systems are outside this spec. |
| D13 | Audit emission | Every profile write emits an `OperatorAuditEntry` with action `PROFILE_CHANGE`. Every forced-escalation event emits a `forced_escalation_triggers` field on the email analysis payload. | Matches kill-switch audit discipline. The operator audit log remains the single source of truth for policy-surface changes. |
| D14 | Kill switch precedence | Kill-switch check stays the outermost gate in every loop entry. Profile resolution runs AFTER the kill-switch check, never as a substitute for it. | Guardrail 12 separation. The profile system is not a kill switch and never claims that surface. |
| D15 | Backward-compatibility | The existing `EmailRiskScoringConfig.enable_ransomware_precursor_overlay` and Phase 1.4 floor lifts remain functional. The profile system layers on top: when overlay is `False`, no detector runs regardless of tier. | No regression on existing fixtures (Month 1 / 2 / 3 Red battery, grok-4 PASS gate). |

Changing any locked decision requires reopening this spec, not a code-level workaround.

---

## §3 Profile Contract

### Tier definitions (v1)

| Tier | Always-on detectors | Tier-gated detectors enabled | High-only detectors enabled | Typical cost shape |
|---|---|---|---|---|
| **LOW** | LLM primary, precursor overlay, header divergence, ghost thread | (none) | (none) | 1 LLM call + cheap deterministic overlays per email. |
| **MEDIUM** | All LOW detectors | Financial State Ledger | (none, v1) | LOW cost + FSL extraction + Vendor Baseline Store reads + 0–N writes per email. |
| **HIGH** | All MEDIUM detectors | Financial State Ledger + future deliberation primitives | Reserved (v2 deliberation, judge pass, devil's-advocate, skeptic pass, OCR, visible reasoning trace) | MEDIUM cost in v1; will rise in v2 as deliberation primitives ship. |

Tier comparison uses integer ranks `LOW=0 < MEDIUM=1 < HIGH=2`. A detector with minimum tier `MEDIUM` runs when `effective_tier_rank >= 1`.

### Routing rule (v1)

For each inbound email:

1. Read the tenant's default profile (or `MEDIUM` if no state file exists).
2. Apply tenant-scoped add-on detector enables (D11 lift-only — add-ons only ever raise the enabled set).
3. Run the always-on (LOW-tier) detectors unconditionally. Their evidence is required to evaluate forced-escalation triggers.
4. Evaluate the four `ForcedEscalationTrigger` rules in §6 against the always-on evidence + operator input.
5. If any trigger fires, raise `effective_profile = HIGH` for this email only. The tenant's stored default is unchanged.
6. Run every tier-gated detector whose minimum tier is `<= effective_profile_rank` AND whose entry is enabled (default or via add-on).
7. Pass the assembled detector outputs to `_overlay_ransomware_precursor` so that the existing max-merge / lift-only path produces the final `risk_score`.

### Visible output

The final `EmailAnalysisPayload` (and the daily digest row) must include:

- `effective_profile`: `"low" | "medium" | "high"`.
- `tenant_default_profile`: the tenant's stored default at scoring time.
- `forced_escalation_triggers`: `tuple[ForcedEscalationTrigger, ...]` (empty when no trigger fired).

This is the audit trail an MSP shows to a client when asked "why did this email get extra scrutiny on a Low-tier account?".

---

## §4 API Contract

### Module: `core/operator_state/security_profile.py`

Public surface:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Iterable, Literal


SecurityProfile = Literal["low", "medium", "high"]


class _SecurityProfileRank(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


DetectorIdentity = Literal[
    "llm_primary",
    "ransomware_precursor_overlay",
    "header_divergence",
    "ghost_thread",
    "financial_state_ledger",
]


ForcedEscalationTrigger = Literal[
    "llm_high_risk_score",
    "header_divergence_strong",
    "ghost_thread_detected",
    "manual_operator_escalation",
]


SalesPlan = Literal["essentials", "plus", "enterprise"]


@dataclass(frozen=True)
class TenantSecurityProfileState:
    tenant_id: str
    profile: SecurityProfile
    addon_detectors: tuple[DetectorIdentity, ...] = ()
    updated_at: datetime | None = None
    updated_by: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class ProfileResolution:
    tenant_default: SecurityProfile
    effective_profile: SecurityProfile
    forced_escalation_triggers: tuple[ForcedEscalationTrigger, ...]
    enabled_detectors: tuple[DetectorIdentity, ...]


@dataclass(frozen=True)
class ForcedEscalationEvidence:
    """Inputs to the forced-escalation evaluator. All fields optional;
    missing evidence simply means that trigger cannot fire on this email."""

    llm_risk_score: int | None = None
    header_divergence_score: int | None = None
    ghost_thread_score: int | None = None
    manual_escalation_requested: bool = False
```

### Functions

```python
def resolve_profile_for_email(
    *,
    tenant_default: SecurityProfile,
    addon_detectors: Iterable[DetectorIdentity],
    evidence: ForcedEscalationEvidence,
) -> ProfileResolution:
    """Pure function. Given a tenant default tier, the tenant's add-on
    enable set, and the always-on detector evidence for one email, return
    the effective tier, the firing forced-escalation triggers, and the
    final enabled detector tuple. Lift-only: the returned
    `effective_profile` rank is always `>=` the `tenant_default` rank."""


def default_profile_for_sales_plan(plan: SalesPlan) -> SecurityProfile:
    """Lookup. Essentials -> LOW, Plus -> MEDIUM, Enterprise -> HIGH."""


def tenant_profile_state_path(
    blackboard_root: Path, tenant_id: str
) -> Path:
    """blackboard_root / 'operator_state' / 'security_profiles' / f'{tenant_id}.json'"""


def load_tenant_profile_state(
    blackboard_root: Path, tenant_id: str
) -> TenantSecurityProfileState:
    """Strict disk-load. Returns `TenantSecurityProfileState(tenant_id, "medium", ())`
    if no file exists. Raises `GovernanceError` on unknown fields, bad enum
    values, or unsafe tenant_id (reused validation from VBS / kill switch)."""


def save_tenant_profile_state(
    blackboard_root: Path,
    state: TenantSecurityProfileState,
    *,
    actor: str,
    reason: str,
) -> None:
    """Atomic `.tmp + rename` write. Appends one `OperatorAuditEntry`
    with action `PROFILE_CHANGE` to the existing operator audit log."""
```

Internal helpers may exist (rank conversion, evidence-to-trigger evaluation, enabled-detector composition), but the public surface is exactly the five functions and five types above.

### Module: `core/scoring/email_risk_scoring_agent.py` integration

The scoring agent gains a single new helper plus a narrow change to `_overlay_ransomware_precursor`. Public surface stays stable:

- `EmailRiskScoringConfig` gains one optional field: `default_profile_when_unset: SecurityProfile = "medium"`. Defaults preserve all existing fixtures byte-identically.
- A new internal helper `_resolve_profile_for_inbound(...)` reads the tenant profile state, runs the always-on detectors, builds `ForcedEscalationEvidence`, calls `resolve_profile_for_email`, and returns the `ProfileResolution` plus the always-on detector outputs to avoid duplicate work.
- `_overlay_ransomware_precursor` accepts the existing `financial_state_ledger_assessment` only when `"financial_state_ledger" in resolution.enabled_detectors`. Otherwise it ignores the assessment, treating that detector as "did not run" — same as today's no-detector path.
- The final `EmailAnalysisPayload.metadata` (or an equivalent visible field) records `effective_profile`, `tenant_default_profile`, `forced_escalation_triggers`. Exact field placement to be finalized in the implementation receipt; spec only requires those three values be readable from the analysis record.

---

## §5 Detector Min-Tier Registration

The `DetectorIdentity` → minimum-tier map is a single locked constant inside `core/operator_state/security_profile.py`:

```python
DETECTOR_MIN_TIER: dict[DetectorIdentity, SecurityProfile] = {
    "llm_primary":                 "low",
    "ransomware_precursor_overlay":"low",
    "header_divergence":           "low",
    "ghost_thread":                "low",
    "financial_state_ledger":      "medium",
}
```

Rules:

- The map is exhaustive over `DetectorIdentity`. A gate test asserts both keys-equal-enum and that every value is a valid `SecurityProfile`.
- Adding a detector requires extending both `DetectorIdentity` and `DETECTOR_MIN_TIER` in the same change. A test will refuse partial extensions.
- Removing a detector requires a spec revision; v1 cannot drop a locked detector.
- Add-on enables (per-tenant) can elevate `financial_state_ledger` onto a LOW tenant, but cannot elevate a detector that does not exist in `DETECTOR_MIN_TIER`.

---

## §6 Forced Escalation Contract

### Closed trigger set (v1)

| Trigger | Source evidence | Threshold | Lift target |
|---|---|---|---|
| `LLM_HIGH_RISK_SCORE` | LLM primary `risk_score` | `>= 80` | `HIGH` |
| `HEADER_DIVERGENCE_STRONG` | `score_header_divergence().score` | `>= 80` | `HIGH` |
| `GHOST_THREAD_DETECTED` | `score_ghost_thread().score` | `> 0` (any non-zero) | `HIGH` |
| `MANUAL_OPERATOR_ESCALATION` | Operator input on this email (boolean) | `True` | `HIGH` |

Each trigger is evaluated independently. Triggers that fire are returned in `ProfileResolution.forced_escalation_triggers`; the effective tier is then `max(tenant_default_rank, HIGH_rank)` = `HIGH` whenever any trigger fires.

### v2-deferred triggers (NOT in v1)

The following triggers would require evidence from detectors that may not run at the tenant's default tier, which would create a chicken-and-egg dependency loop. They are explicitly deferred to v2 and require their own spec entries:

- `FINANCIAL_STATE_DELTA` (depends on FSL running, which currently requires MEDIUM+)
- `HIGH_VALUE_INVOICE` (requires dollar-amount extraction that doesn't ship in v1)
- `PRIOR_VENDOR_FRAUD_FLAG` (requires a vendor reputation surface that doesn't exist)
- `FRESH_BASELINE_VENDOR` (requires VBS age-of-first-seen surface — not exposed today)
- `COMBINED_BEC_SIGNALS` (requires a multi-signal combiner)

v1 explicitly does NOT include these. Attempting to wire them anyway in implementation is a spec divergence.

### Lift-only invariant

`resolve_profile_for_email` MUST satisfy:

```python
assert _rank(resolution.effective_profile) >= _rank(resolution.tenant_default)
```

A gate test pins this for all 3 × 2^4 = 48 (tenant_default, trigger-firing-combination) inputs.

---

## §7 Gate Tests

Implementation must pass all tests below before §4 can be claimed closed.

1. **Closed enums.** `SecurityProfile`, `DetectorIdentity`, `ForcedEscalationTrigger`, `SalesPlan` each iterate exactly the values locked in §2 + §3 + §5 + §6. No string outside those sets is accepted by the resolver.
2. **Rank ordering.** `_rank("low") < _rank("medium") < _rank("high")`.
3. **Default-when-unset.** `load_tenant_profile_state(blackboard_root, "tenant_x")` on a fresh blackboard returns `profile == "medium"`, `addon_detectors == ()`.
4. **Detector min-tier registry exhaustive.** `set(DETECTOR_MIN_TIER.keys()) == set(get_args(DetectorIdentity))` and every value is a valid `SecurityProfile`.
5. **LOW resolves to LOW detectors only.** A Low tenant with no escalation evidence returns `enabled_detectors` equal to the LOW-tier set; `financial_state_ledger` is NOT in the tuple.
6. **MEDIUM resolves to LOW + MEDIUM detectors.** A Medium tenant with no escalation returns `enabled_detectors` including `financial_state_ledger`.
7. **HIGH resolves to MEDIUM detectors in v1.** A High tenant returns the same enabled set as Medium (no HIGH-only detectors exist yet); future HIGH-only detectors must extend this test.
8. **Add-on lift.** A LOW tenant with `addon_detectors=("financial_state_ledger",)` returns `enabled_detectors` containing `financial_state_ledger` even with no escalation triggered.
9. **Add-on cannot disable.** Building a `TenantSecurityProfileState` does not expose a "disable" list. A gate test asserts there is no path to remove a detector that the effective tier would enable.
10. **Forced trigger: LLM high score.** Evidence with `llm_risk_score=85`, all other evidence at defaults, returns `effective_profile="high"` and `forced_escalation_triggers=("llm_high_risk_score",)` regardless of `tenant_default`.
11. **Forced trigger: header divergence strong.** Evidence with `header_divergence_score=85` returns `forced_escalation_triggers=("header_divergence_strong",)`.
12. **Forced trigger: ghost thread detected.** Evidence with `ghost_thread_score=10` returns `forced_escalation_triggers=("ghost_thread_detected",)`.
13. **Forced trigger: manual escalation.** Evidence with `manual_escalation_requested=True` returns `forced_escalation_triggers=("manual_operator_escalation",)`.
14. **Multiple triggers.** Two triggers firing return both in `forced_escalation_triggers`, deduplicated, in a stable order. Effective profile is still `HIGH` (no double-lift).
15. **Lift-only invariant.** For every combination of `tenant_default ∈ {low,medium,high}` and every subset of the four trigger booleans (48 cases), `rank(effective_profile) >= rank(tenant_default)`.
16. **Tenant isolation.** Writing `tenant_a` to LOW and then reading `tenant_b` returns the default MEDIUM. State files are per-tenant; one tenant's file is never read for another tenant.
17. **Audit row on profile change.** `save_tenant_profile_state(..., actor="matt", reason="demo")` appends exactly one `OperatorAuditEntry` to the existing operator audit log with action `PROFILE_CHANGE`, the new profile, and the actor/reason. Existing kill-switch audit entries are unaffected.
18. **Forced-escalation visibility.** When forced escalation fires, the resulting analysis record contains `effective_profile="high"`, the firing trigger tuple, and the original `tenant_default_profile`.
19. **Sales-plan mapping.** `default_profile_for_sales_plan("essentials") == "low"`, `... "plus" == "medium"`, `... "enterprise" == "high"`. No other inputs are accepted.
20. **Kill-switch precedence.** With the production kill switch engaged, `run_email_risk_scoring_cycle` raises `KillSwitchEngaged` BEFORE reading any tenant profile. Gate test patches `load_tenant_profile_state` with a spy that must never be called.
21. **Backward compatibility — overlay off.** With `enable_ransomware_precursor_overlay=False` (existing config field), the scoring agent does not consult the profile resolver and produces byte-identical output to current Month 1 / 2 / 3 fixtures.
22. **Backward compatibility — profile field absent.** Existing `EmailAnalysisPayload` schemas without `effective_profile`/`tenant_default_profile`/`forced_escalation_triggers` continue to validate. The new fields are additive and optional in the schema (Phase 1.6 schema extension; one schema migration test pin).
23. **Cost monotonicity (steady state).** A fake scoring cycle with no escalation triggers shows: detector-call count for LOW ≤ detector-call count for MEDIUM ≤ detector-call count for HIGH. The exact counts are pinned in this test so future detector additions cannot silently regress the cost contract.
24. **Cost ceiling under escalation.** Even when forced escalation fires on a LOW tenant, the detector-call count does not exceed the HIGH steady-state count. (Forced escalation lifts the set; it does not duplicate detectors.)
25. **No raw value leakage.** None of `effective_profile`, `tenant_default_profile`, `forced_escalation_triggers`, or the audit row contain raw email body, raw financial strings, or PII beyond the actor / reason fields already permitted by the kill-switch audit schema.
26. **Tenant id validation.** Path-separator, whitespace, uppercase, and empty tenant ids raise `GovernanceError` in both `load_tenant_profile_state` and `save_tenant_profile_state`. Reuses VBS tenant validation; gate test pins identical error wording.
27. **Strict disk load.** A tampered `security_profiles/<tenant>.json` (unknown field, bad enum, wrong type) raises `GovernanceError`. Same strictness as kill-switch state load.
28. **No direct Blackboard write.** The profile module never calls orchestrator route functions. All audit emission goes through `core/operator_state/audit.py` (existing operator audit pipeline).
29. **No new persistent state outside operator_state/.** A test scans the project for new SQLite / JSON / DB writes introduced by this build and confirms they are confined to `blackboard_root/operator_state/security_profiles/`.
30. **Grok audit package target.** `audit_tools/grok_audit_runner.py` is extended with a `tiered_detection_intensity` target before the implementation receipt can claim closure. The package's file list is asserted by a direct gate test (matches the FSL §7-#22 pattern).

If any test in this list does not pass, the implementation receipt is not allowed to claim §4 closed.

---

## §8 Boundaries & Safety

| Concern | Enforcement |
|---|---|
| Guardrail 11 Blue Loop write surface | Profile state lives in `operator_state/`, NOT in `production_state/`. The four mutable production surfaces are unchanged. |
| Guardrail 12 kill-switch separation | Kill-switch check stays the outermost gate. Profile resolution runs strictly after. Operator audit log is shared, but action types are distinct (`PROFILE_CHANGE` vs kill-switch actions). |
| Tenant isolation | Per-tenant file under `operator_state/security_profiles/<tenant_id>.json`. Tenant id validation reuses VBS rules. |
| Lift-only invariant | Forced escalation can only raise the tier. Add-ons can only enable, never disable. Both pinned by gate tests #9, #15, #24. |
| Cost runaway | Cost-monotonicity gate test #23 + ceiling gate test #24 lock the call-count shape. New detectors cannot silently regress. |
| Alert fatigue from forced escalation | Trigger thresholds (LLM ≥ 80, header divergence ≥ 80, ghost thread > 0, manual) are deliberately conservative — escalation should be rare on routine mail. Tunable only by re-spec. |
| MSP misconfiguration | Every profile change writes an audit row with actor + reason. An MSP downgrading a tenant to LOW leaves a permanent trail. |
| Schema regression | Backward-compat gate tests #21 + #22 pin existing fixtures and schema. |
| External calls | None. The profile system is pure logic + on-disk state inside the existing operator-state surface. |

---

## §9 Downstream Integration

### Email scoring agent

`run_email_risk_scoring_cycle` and `score_one_email_payload` both gain the profile resolution step described in §4. The integration is minimal because all five v1 detectors are already callable from a single path (`_overlay_ransomware_precursor`); the new code only decides which of those calls actually happens.

### Daily digest / report

Every analysis row rendered in the digest gains three visible fields:

- `Profile: <effective_profile>`
- `Tenant default: <tenant_default_profile>` (only shown when different from `effective_profile`)
- `Escalated by: <forced_escalation_triggers>` (only shown when non-empty)

This is the audit trail an MSP shows a client when explaining why a Low-tier mailbox saw extra scrutiny.

### Sales formation

The `default_profile_for_sales_plan` lookup is consumed by onboarding scripts and the Discovery Questionnaire surface. The mapping is locked here (§2 D12) so sales copy, pricing pages, and the `Add_Ons_Pricing.md` table can cite this spec by section number.

### Future deliberation primitives (v2)

When the deliberation / judge / devil's-advocate primitives ship, they will:

1. Extend `DetectorIdentity` with their identifiers (new §11-signed spec required).
2. Extend `DETECTOR_MIN_TIER` to map them to `HIGH`.
3. Inherit the §6 forced-escalation lift so a Low tenant facing a risky email still gets full deliberation on that email.

No code in v1 needs to anticipate the v2 detectors beyond the closed-enum gate test, which will refuse to compile when the enum and the registry drift apart.

---

## §10 V2 Deferrals & Explicit Non-Goals

| Deferral | Rationale |
|---|---|
| HIGH-only deliberation primitives (judge, devil's-advocate, skeptic, OCR, visible reasoning trace) | Each is a separate §11-signed spec. v1 reserves `HIGH` as a tier but ships no HIGH-only detector. |
| `FINANCIAL_STATE_DELTA` forced-escalation trigger | Requires FSL to run before the trigger can fire; creates a chicken-and-egg cycle for Low tenants. Deferred until v2 introduces a two-pass routing or makes FSL `LOW`-tier with a cost-gated config. |
| `HIGH_VALUE_INVOICE` trigger | Requires deterministic dollar-amount extraction that does not ship in v1. |
| `PRIOR_VENDOR_FRAUD_FLAG` trigger | Requires a vendor reputation surface that does not exist yet. |
| `COMBINED_BEC_SIGNALS` trigger | Requires a multi-signal combiner specification. |
| Self-service MSP UI for profile changes | Operator-only writes in v1, matching kill-switch convention. The MSP self-service surface is its own product decision. |
| Automatic profile downgrade after quiet period | Explicit operator action only. No silent state transitions. |
| Per-rule sensitivity dialing | v1 is detector-on / detector-off. Per-rule thresholds remain detector-internal. |
| Pricing / billing engine | Out of runtime scope. The sales-plan lookup is documentation only. |
| Cross-tenant reputation or rule sharing | Tenant isolation invariant prohibits this in v1. |

---

## §11 Lockdown Signature

This spec is locked when the block below is filled in. The implementation receipt for the detector must cite this file by section number.

```text
LOCKED BY:  Matt (operator)
LOCK DATE:  2026-05-24
COMMENTS:   All §2 architectural decisions (D1-D15) locked end-to-end during
            the 2026-05-24 spec-first session. Highlights:
              - Pure types + resolver live in
                core/operator_state/security_profile.py; per-tenant state at
                blackboard_root/operator_state/security_profiles/<tenant>.json
                (Guardrail 12 separation; Guardrail 11 surfaces unchanged).
              - Three-tier closed enum: low / medium / high. Integer ranks
                LOW=0 < MEDIUM=1 < HIGH=2.
              - Default tenant posture when no state file exists = MEDIUM.
                A LOW tenant must be explicitly written by the operator.
              - Closed DetectorIdentity enum (v1) matches the five detector
                slots already wired into _overlay_ransomware_precursor:
                llm_primary, ransomware_precursor_overlay, header_divergence,
                ghost_thread, financial_state_ledger.
              - LOW set = LLM primary + precursor overlay + header
                divergence + ghost thread. MEDIUM adds FSL. HIGH is reserved
                in v1; no HIGH-only detector ships before its own §11 spec.
              - Closed ForcedEscalationTrigger enum (v1, four triggers):
                llm_high_risk_score (>=80), header_divergence_strong (>=80),
                ghost_thread_detected (>0), manual_operator_escalation.
                Five additional triggers (financial_state_delta,
                high_value_invoice, prior_vendor_fraud_flag,
                fresh_baseline_vendor, combined_bec_signals) are explicit
                v2 deferrals listed in §10.
              - Lift-only invariant: forced escalation can ONLY raise the
                effective tier; add-on detectors can ONLY enable, never
                disable. Both pinned by gate tests #9, #15, #24.
              - Sales-plan default mapping locked (Option C):
                essentials -> low, plus -> medium, enterprise -> high.
              - Audit emission: every profile write appends one
                OperatorAuditEntry with action PROFILE_CHANGE; every forced
                escalation is recorded on the analysis payload. Operator
                audit log remains the single source of truth.
              - Kill switch (Guardrail 12) stays the outermost gate at
                every loop entry. Profile resolution runs strictly AFTER
                the kill-switch check, never as a substitute for it.
              - Backward compat: enable_ransomware_precursor_overlay=False
                must still produce byte-identical output to existing
                Month 1 / Month 2 / Month 3 fixtures and the grok-4 PASS
                gate. New analysis fields are additive + optional.
              - §7 30-test gate is the closure contract. Partial
                implementations do NOT close §4. Cost-monotonicity (#23)
                and cost-ceiling-under-escalation (#24) lock the call-count
                shape so future detector additions cannot silently regress
                the cost contract.
              - Grok independent-audit target `tiered_detection_intensity`
                must be wired into audit_tools/grok_audit_runner.py BEFORE
                the implementation is claimed closed (§7 test #30).
              - Implementation work does NOT begin until Matt issues the
                explicit "start build" signal in chat.
```

Once signed:

- Every implementation receipt must cite this file by section number.
- Any deviation from a §2 locked decision requires a new spec revision.
- The §7 gate test list is the closure contract.
- Implementation still requires Matt's explicit `start build` signal after signature.
