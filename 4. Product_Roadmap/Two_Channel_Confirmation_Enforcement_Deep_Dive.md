# Two-Channel Confirmation Enforcement — Implementation Spec (Deep Dive)

**Status:** §11 SIGNED 2026-05-24 by Matt Nichol; implementation in progress.  
**Authors:** Matt (operator decisions) + AI scribe (capture).  
**Last reviewed:** 2026-05-24 UTC.  
**Source-of-truth links:** `think_sheet.md` (Two-channel confirmation enforcement promote row + 2026-05-24 stress-test answers), `4. Product_Roadmap/Financial_State_Ledger_Deep_Dive.md`, `4. Product_Roadmap/Document_Metadata_Fingerprinting_Deep_Dive.md`, `PROJECT_GUARDRAILS.md`.

This is the specification contract for the Two-Channel Confirmation Enforcement workflow layer v1. Once signed, every implementation receipt must cite this file by section number.

---

## §0 Purpose

When a deterministic detector (Financial State Ledger, Document Metadata Fingerprinting, etc.) raises a finding that *requires out-of-band verification before money moves*, NorthStar's runtime must:

1. Record an append-only `pending` two-channel-confirmation event in the Blackboard so the daily digest can surface it as an unresolved control task.
2. Allow an operator (MSP / bookkeeper) to later record a confirmation outcome (`confirmed`, `rejected`, `unable_to_verify`, `expired`) along with which channel they used and who verified it.
3. Guarantee the audit trail is append-only (no edits, no deletes) and never lowers an existing risk floor (`lift-only`).
4. Honor the production kill switch on **mutating entry points** (request + outcome), and per-tenant isolation on all entry points (mutating and read). Read-only inspection (`list_pending_confirmations`, `summarize_confirmation_status`) remains available during a kill-switched incident so an operator can still see what is pending.

This is the workflow/audit layer that converts an alert into a recorded control. It is the Stage-A version: no portal, no shared secrets, no challenge/response. It only formalizes "did a human actually verify via a previously-known channel?" as a recorded, auditable event.

---

## §1 Scope

### In scope (v1)

- New Blackboard `RecordType.TWO_CHANNEL_CONFIRMATION` with one Pydantic payload model `TwoChannelConfirmationPayload`.
- New module `core/workflows/two_channel_confirmation.py` exposing:
  - `record_confirmation_request(...)` — called by the scoring agent (or test harness) when a finding flags `requires_out_of_band_verification=True`. Writes a `pending` event.
  - `record_confirmation_outcome(...)` — called by the operator-facing path. Writes a follow-up `outcome` event keyed by `finding_id`.
  - `list_pending_confirmations(...)` — returns finding_ids that have a `pending` event with no `outcome` event yet, for digest rendering.
  - `summarize_confirmation_status(...)` — returns the current confirmation state for a single `finding_id`.
- Bounded text fields on every operator-supplied string (operator identity, channel description, reason). Length limits enforced via `StrictModel` validators.
- Closed enums for `outcome_status` and `channel_kind`.
- Kill-switch gating on every entry point (request and outcome).
- Per-tenant isolation through the existing Blackboard tenant directory layout.
- Lift-only invariant: a `confirmed` outcome **does not** lower the recommended risk floor; the runtime never trusts a self-attested "I verified it" to downgrade risk.
- 18+ gate tests in `tests/test_two_channel_confirmation.py`.

### Out of scope (v1)

- Shared cryptographic secrets, challenge/response tokens, or any cryptographic vendor identity.
- A NorthStar Portal or web UI.
- Vendor-side workflow (vendor never authenticates themselves to NorthStar in v1).
- Automated outbound email / SMS / phone calls.
- Mutation or deletion of confirmation records.
- Changing the `recommended_risk_floor` based on a confirmation outcome.

---

## §2 Locked Architectural Decisions

| # | Decision | Locked Value | Rationale |
|---|---|---|---|
| D1 | Runtime location | `core/workflows/two_channel_confirmation.py` (resolved as `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/workflows/two_channel_confirmation.py` on disk, mirroring every other runtime module in this repo) | New `core/workflows/` package for workflow/audit primitives, mirrors `core/production_state/` and `core/scoring/`. |
| D2 | Persistent storage | Existing Blackboard append-only event log (no new SQLite store) | Stage-A constraint; reuses the per-tenant blackboard layout and tooling. |
| D3 | Record type | New `RecordType.TWO_CHANNEL_CONFIRMATION` | Keeps confirmation events distinct from generic `WORKFLOW_TRIGGER` so digest queries are cheap. |
| D4 | Payload model | `TwoChannelConfirmationPayload(StrictModel)` with closed `event_type`, `outcome_status`, `channel_kind` enums | Closed enums prevent free-form drift. |
| D5 | Event family | One payload, two `event_type` values: `pending` and `outcome` | Two-event finite-state machine; no edits, no closures. |
| D6 | finding_id contract | Caller-supplied opaque string, length 1..128, validated against `[A-Za-z0-9_\-:.]+`, **and** must not equal `.`, `..`, or start/end with `.` (defensive guards against relative-path style tokens) | Lets the scoring layer key on `(detector, signal_hash)` style identifiers without coupling models, while refusing tokens that resemble path-traversal segments. |
| D7 | Lift-only invariant | A `confirmed` outcome does NOT lower any risk floor or recommended action | Defends against the "checkbox security" failure mode flagged in the think sheet pre-mortem. |
| D8 | Append-only | No mutation, no delete, no superseding payload field beyond a chained `outcome` event | Aligns with Blackboard's existing append-only contract. |
| D9 | One outcome per request | The second `outcome` event for the same `finding_id` raises `GovernanceError` | Prevents whitewashing a previous `rejected` with a later `confirmed`. |
| D10 | Channel kinds | Closed enum: `previously_known_phone`, `previously_known_in_person`, `previously_known_video_call`, `previously_known_internal_system`, `other_documented` | Forces the operator to name the channel; "other" still requires a non-empty reason. |
| D11 | Outcome statuses | Closed enum: `confirmed`, `rejected`, `unable_to_verify`, `expired` | `expired` is for an automated daily-digest sweep in a future lane; v1 only writes it when an operator explicitly chooses it. |
| D12 | Kill switch | Production kill switch blocks the two mutating entry points (`record_confirmation_request`, `record_confirmation_outcome`). Read-only helpers (`list_pending_confirmations`, `summarize_confirmation_status`) stay available so operators can still see pending control tasks during a kill-switched incident. | Mirrors Vendor Baseline Store / FSL kill-switch posture on writes; preserves incident-time visibility on reads. |
| D13 | Tenant isolation | Every call requires `tenant_id`; record is written under that tenant's Blackboard | Mirrors every other per-tenant primitive. |
| D14 | Data minimization | No raw email body, vendor address, account numbers, or finding raw values in the payload. Operator identity is length-bounded (1..128) and treated as a label, not PII. | Same minimization posture as FSL and Document Metadata. |
| D15 | API contract | All functions return frozen dataclasses; mutation forbidden | Same pattern as `vendor_baseline.check_signal` / `assess_financial_state_delta`. |
| D16 | Receipt anchors | `PROJECT_HANDSHAKE.md` + `PROGRESS.md` Task 34 | Auditor anchors for `grok_audit_runner.py two_channel_confirmation`. |

---

## §3 Schema Additions (`core/blackboard/models.py`)

```python
class RecordType(str, Enum):
    ...
    TWO_CHANNEL_CONFIRMATION = "two_channel_confirmation"


TwoChannelEventType = Literal["pending", "outcome"]
TwoChannelOutcomeStatus = Literal["confirmed", "rejected", "unable_to_verify", "expired"]
TwoChannelChannelKind = Literal[
    "previously_known_phone",
    "previously_known_in_person",
    "previously_known_video_call",
    "previously_known_internal_system",
    "other_documented",
]


class TwoChannelConfirmationPayload(StrictModel):
    event_type: TwoChannelEventType
    finding_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    detector: str = Field(min_length=1, max_length=128)
    recommended_action: Literal["needs_review"]
    risk_floor: int = Field(ge=0, le=100)
    requested_at: datetime | None = None     # pending only
    requested_by: str | None = Field(default=None, max_length=128)
    outcome_at: datetime | None = None       # outcome only
    outcome_by: str | None = Field(default=None, max_length=128)
    outcome_status: TwoChannelOutcomeStatus | None = None
    channel_kind: TwoChannelChannelKind | None = None
    channel_description: str | None = Field(default=None, max_length=256)
    reason: str | None = Field(default=None, max_length=512)
```

`finding_id` is validated against `re.compile(r"^[A-Za-z0-9_\-:.]+$")` at the workflow layer, not at the Pydantic layer, so callers see a `GovernanceError` instead of a `ValidationError`.

---

## §4 API Contract (`core/workflows/two_channel_confirmation.py`)

```python
@dataclass(frozen=True)
class ConfirmationRecord:
    finding_id: str
    tenant_id: str
    detector: str
    recommended_action: Literal["needs_review"]
    risk_floor: int
    requested_at: datetime
    requested_by: str
    outcome_at: datetime | None = None
    outcome_by: str | None = None
    outcome_status: TwoChannelOutcomeStatus | None = None
    channel_kind: TwoChannelChannelKind | None = None
    channel_description: str | None = None
    reason: str | None = None


def record_confirmation_request(
    *,
    tenant_id: str,
    finding_id: str,
    detector: str,
    risk_floor: int,
    requested_by: str,
    requested_at: datetime,
    blackboard_root: Path | None = None,
) -> ConfirmationRecord: ...


def record_confirmation_outcome(
    *,
    tenant_id: str,
    finding_id: str,
    outcome_status: TwoChannelOutcomeStatus,
    outcome_by: str,
    outcome_at: datetime,
    channel_kind: TwoChannelChannelKind | None = None,
    channel_description: str | None = None,
    reason: str | None = None,
    blackboard_root: Path | None = None,
) -> ConfirmationRecord: ...


def list_pending_confirmations(
    *,
    tenant_id: str,
    blackboard_root: Path | None = None,
) -> tuple[ConfirmationRecord, ...]: ...


def summarize_confirmation_status(
    *,
    tenant_id: str,
    finding_id: str,
    blackboard_root: Path | None = None,
) -> ConfirmationRecord | None: ...
```

### Behavior

1. `record_confirmation_request` writes one `TWO_CHANNEL_CONFIRMATION` record with `event_type="pending"`. Raises `GovernanceError` if:
   - `finding_id` already has any prior event (pending or outcome) for this tenant.
   - `risk_floor` is outside `[1, 100]` (must be a positive floor since this is only called on `needs_review` findings).
   - Any required string is empty or exceeds its length limit.
   - Kill switch is engaged.

2. `record_confirmation_outcome` writes one `TWO_CHANNEL_CONFIRMATION` record with `event_type="outcome"`. Raises `GovernanceError` if:
   - There is no prior `pending` event for this `finding_id` and tenant.
   - There is already an `outcome` event for this `finding_id` and tenant.
   - `outcome_status="confirmed"` is passed without a `channel_kind`.
   - `channel_kind="other_documented"` is passed without a non-empty `reason`.
   - Outcome timestamp is earlier than the corresponding pending timestamp.
   - Kill switch is engaged.

3. `list_pending_confirmations` reads only this tenant's Blackboard, returns `ConfirmationRecord` instances for `finding_id`s that have a `pending` event but no `outcome` event yet, sorted by `requested_at` ascending.

4. `summarize_confirmation_status` returns the most informative single record for one `finding_id` (the `outcome` event if present, else the `pending` event, else `None`).

5. None of these functions mutate any existing Blackboard record; they only append.

---

## §5 Lift-Only Invariant

The scoring overlay never reads two-channel confirmation events to lower a recommended risk floor. `confirmed` is purely audit. A future lane may surface `unable_to_verify` and `rejected` as additional risk lifts, but v1 is strictly append-only audit with no scoring effect.

This is enforced by the test suite (a `confirmed` outcome does not change `recommended_risk_floor`), and by the absence of any read from `core/scoring/email_risk_scoring_agent.py` into this module.

---

## §6 Gate Tests (`tests/test_two_channel_confirmation.py`)

Implementation must pass all of these before §3 closure.

1. Public API surface locked (`__all__`, frozen dataclass).
2. `record_confirmation_request` writes one `TWO_CHANNEL_CONFIRMATION` record with `event_type="pending"`.
3. `record_confirmation_request` raises `GovernanceError` on duplicate `finding_id`.
4. `record_confirmation_request` raises `GovernanceError` on invalid `finding_id` characters.
5. `record_confirmation_request` raises `GovernanceError` on `risk_floor` outside `[1, 100]`.
6. `record_confirmation_request` raises `KillSwitchEngaged` when production kill switch is engaged.
7. `record_confirmation_outcome` writes one `outcome` event after a `pending` event.
8. `record_confirmation_outcome` raises `GovernanceError` without a prior `pending` event.
9. `record_confirmation_outcome` raises `GovernanceError` on a second `outcome` event for the same `finding_id`.
10. `record_confirmation_outcome` raises `GovernanceError` when `outcome_status="confirmed"` is passed without `channel_kind`.
11. `record_confirmation_outcome` raises `GovernanceError` when `channel_kind="other_documented"` is passed without `reason`.
12. `record_confirmation_outcome` raises `GovernanceError` when `outcome_at < requested_at`.
13. `record_confirmation_outcome` raises `KillSwitchEngaged` when production kill switch is engaged.
14. `list_pending_confirmations` returns only `finding_id`s with a `pending` and no `outcome`, sorted by `requested_at`.
15. `list_pending_confirmations` filters by tenant (tenant A cannot see tenant B's pending items).
16. `summarize_confirmation_status` returns `None` for an unknown `finding_id`.
17. `summarize_confirmation_status` returns the `outcome` record once present, otherwise the `pending` record.
18. Lift-only invariant: writing a `confirmed` outcome does not produce any risk score change anywhere; the helper `recommended_risk_floor` field on the record is preserved from the pending event.
19. Audit payload contains no raw email content, no vendor address, no account number, and no finding raw value.
20. `RecordType.TWO_CHANNEL_CONFIRMATION` is registered in `_RECORD_TYPE_TO_PAYLOAD`.
21. `grok_audit_runner.py` exposes `two_channel_confirmation` audit target.

---

## §7 Boundaries & Safety

| Concern | Enforcement |
|---|---|
| Tenant isolation | Every entry point requires `tenant_id`; reads/writes only touch that tenant's Blackboard. |
| Kill switch | Production kill switch blocks both entry points. |
| Data minimization | No raw finding values, no vendor email, no account numbers in payload. |
| Append-only | No mutation; second `outcome` event raises. |
| Scope creep | No portal, no shared secrets, no challenge/response, no scoring effect. |
| External calls | None. |

---

## §8 §11 Lockdown Signature

**Signed by:** Matt Nichol  
**Date:** 2026-05-24  
**Decisions locked:** D1–D16 above; Stage-A report/audit only; no portal; no scoring effect; append-only Blackboard records; closed enums for `event_type`, `outcome_status`, `channel_kind`; lift-only.

Implementation may proceed against this contract.
