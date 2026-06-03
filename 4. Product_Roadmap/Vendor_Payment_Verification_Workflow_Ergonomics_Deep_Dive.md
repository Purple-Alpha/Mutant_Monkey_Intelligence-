# Vendor-Payment Verification Workflow Ergonomics — Deep Dive

**Status:** DRAFT (pre-§11). Authored 2026-06-03 by Cursor (Claude) on Matt Nichol's instruction. No runtime code in this artifact. No workflow-engine implementation in this artifact. §11 signature blank by design; only Matt may sign.

**Scope reminder:** Specifies the **operator-side disposition workflow** for recording what a human did after NorthStar flagged a vendor-payment change for out-of-band verification. It is the workflow-ergonomics layer that the Financial State Ledger / Delta Tripwire spec explicitly deferred (`Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` §1 out-of-scope: "A portal, confirmation UI, or workflow state machine"). It does **not** add a new detector, does **not** perform autonomous payment action, and does **not** claim NorthStar is compliant, certified, insurer-approved, bulletproof, or fraud-proof.

**Selected by:** Matt Nichol on 2026-06-03 to close the single formal open gap recorded in `CURRENT_STATE_MAP.md` ("Open gap — verification workflow ergonomics for vendor-payment changes: verified / unresolved / false-positive / follow-up-needed, with evidence and retest linkage"). Verbatim operator intent is preserved in the corresponding `PROJECT_ACTIVITY_LOG.md` entry.

---

## §0 Purpose

A Delta Tripwire finding tells an operator *one thing*: a previously-unseen payment destination appeared for a known vendor, so it must be verified through a previously-known channel before money moves (`Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` D10). The detector then stops. It does not record what the human found when they made that out-of-band call.

That recording gap is the problem this spec closes. Without a disposition surface:

- the same finding can resurface with no memory that a human already cleared it,
- a false flag never feeds back into the false-positive correction loop (`CURRENT_STATE_MAP.md` "False-positive / false-negative correction evidence loop"),
- an MSP cannot show a client (or, later, an underwriter) that the flag was actually chased down, and
- nothing distinguishes "we verified this is a legitimate banking change" from "we tried and could not reach the vendor."

This spec defines a **four-value disposition enum**, the **evidence each disposition must carry**, and the **retest / re-check linkage** that ties a disposition back to the finding it resolves and forward to any follow-up. The disposition is a *record of a human decision*, never an autonomous NorthStar action.

---

## §1 Scope

### In scope (v1)

- A closed four-value disposition enum: `verified`, `unresolved`, `false_positive`, `follow_up_needed`.
- A per-finding disposition record: one open disposition per `(tenant_id, finding_id)`, append-only revisions.
- Structured evidence fields per disposition (out-of-band channel used, what was confirmed, who recorded it) — no chain-of-thought, no raw financial strings, no PII.
- Retest / re-check linkage: a disposition references the finding it resolves and, when the disposition is non-terminal, the follow-up item it spawns.
- A `false_positive` disposition's linkage into the existing false-positive / false-negative correction evidence loop and the Email Security Testing & Evidence Framework failure-card pattern (`Email_Security_Testing_Evidence_Framework_Deep_Dive.md` §9.4 / §9.5), recorded by reference, not duplicated.
- An append-only audit-trail event set for disposition open / revise / close.
- A digest/report-friendly one-line rendering of disposition state for the daily digest and monthly report surfaces.

### Out of scope (v1)

- Any new detector or scoring logic. This layer consumes Delta Tripwire / vendor-payment-change findings; it does not produce risk scores.
- Autonomous payment action: approving, blocking, releasing, holding, or reversing a payment. NorthStar records the human's disposition; the human (operator or tenant) decides whether to pay.
- A graphical portal or confirmation UI. v1 is a structured record surface, consistent with the FSL deferral. Rendering technology is a separate operator decision.
- Bank-account ownership verification, vendor KYB lookup, payment-rail validation, or any outbound network call to confirm a destination.
- Replacing or merging with the Two-Channel Confirmation Enforcement mechanism. v1 sits beside it; the relationship is §10 Q2.
- Persisting raw financial identifiers anywhere. Findings already carry only hashes / redacted display (`Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` D13); this layer inherits that and never re-introduces raw values.
- Cross-tenant disposition sharing or reputation. Tenant isolation is preserved.

### §1.3 Safety boundaries (the workflow MUST NOT)

- **MUST NOT** mark any payment as safe, approved, blocked, confirmed, released, or reversed. A disposition records a human's verification outcome; it is not a payment instruction and is not autonomous action.
- **MUST NOT** store, transmit, or render raw financial strings (routing / account / IBAN / SWIFT / portal token) or any PII in disposition records, evidence fields, audit events, or rendered output. It references the finding by `finding_id` and inherits the finding's hash-only / redacted surface.
- **MUST NOT** expose chain-of-thought. Evidence fields are structured strings only.
- **MUST NOT** be treated as operator authorization. A disposition of `verified` does not authorize a commit, a queue promotion, a §11 signature, or a payment release. It informs; Matt (or the tenant) decides.
- **MUST NOT** make a compliance / insurance claim outside the carve-outs in `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md`. Forbidden-language scope inherited verbatim.

---

## §2 Locked Design Decisions

Advisory until §11 is signed; immutable thereafter except by explicit operator-instructed revision.

- **D1. Disposition enum is exactly four values** — `verified`, `unresolved`, `false_positive`, `follow_up_needed`. No fifth value, no collapsing. Meanings are fixed in §3.
- **D2. One open disposition per `(tenant_id, finding_id)`.** A finding has at most one open disposition at a time. Re-dispositioning appends a new revision that supersedes the prior one; history is never overwritten (append-only).
- **D3. Every disposition carries mandatory structured evidence.** Minimum: `verification_channel` (closed enum, §5.2), `what_was_confirmed` (<=280 chars, structured summary, no chain-of-thought), `recorded_by` (operator/reviewer identifier, §10 Q5), `recorded_at_utc`. A disposition missing any mandatory field is `not_eligible_for_closure`.
- **D4. No raw financial strings, no PII, ever.** Inherits FSL D13. Disposition records reference `finding_id` and the finding's existing redacted/hash surface; they never re-derive or store the raw destination.
- **D5. No autonomous payment action.** Inherits FSL D11. The workflow records a human outcome; it never sets a payment to safe / approved / blocked / released.
- **D6. `verified` and `false_positive` are terminal; `unresolved` and `follow_up_needed` are non-terminal.** A non-terminal disposition MUST spawn a follow-up item with a `prior_disposition_ref` back-link (retest linkage). A terminal disposition closes the finding's open state.
- **D7. `false_positive` links into the correction loop.** A `false_positive` disposition MUST record a `correction_loop_ref` (nullable until populated) that points at the false-positive / false-negative correction evidence record or Email Security Testing & Evidence Framework failure card opened for it. v1 records the linkage; it does not itself run the correction. (Exact auto-open behaviour is §10 Q4.)
- **D8. Disposition does not authorize operator action.** Inherits the framework discipline: "all verified" is not authorization to ship, promote, sign, or release payment.
- **D9. Audit trail is append-only.** Open / revise / close emit append-only events (§6). No event is mutated or deleted. Reads are not audited.
- **D10. Tenant isolation is preserved.** Disposition records are per-tenant. No cross-tenant disposition data crosses the boundary (`VISION.md` non-negotiable 4 / Guardrail 11).
- **D11. Forbidden-language enforcement is identical to NorthStar's existing standard.** Disposition text, evidence fields, rendered output, and audit events all in-scope for the inherited forbidden-vocabulary lint (`Compliance_and_Trend_Watch_Process.md`).
- **D12. Kill switch precedence preserved.** If the kill switch is engaged (Guardrail 12), the disposition surface is read-only; no new disposition or revision is written while halted.

Changing any locked decision requires reopening this spec, not a code-level workaround.

---

## §3 Disposition State Model

Every disposition for a finding carries exactly one of these four values:

- **`verified`** *(terminal)* — A human confirmed the payment change through a previously-known vendor channel (not the email that introduced it) and found it legitimate. Records which channel and what was confirmed. Closes the finding's open state. Does **not** mean "safe to pay" as an autonomous claim; it means a human verified and recorded the outcome.
- **`unresolved`** *(non-terminal)* — A human attempted verification but could not reach a definitive answer (vendor unreachable, contact bounced, answer ambiguous). Spawns a follow-up item. The finding stays open.
- **`false_positive`** *(terminal)* — A human determined the flag did not correspond to a real payment-destination change (e.g., the "new" destination was a previously-used account the baseline had aged out, a formatting artifact, or an internal test). Records a `correction_loop_ref` so the over-flag feeds the correction evidence loop. Closes the finding's open state.
- **`follow_up_needed`** *(non-terminal)* — A human triaged the finding and determined a specific next action is required before disposition (e.g., await the vendor's written confirmation, escalate to the client's finance lead). Spawns a follow-up item naming the awaited action. The finding stays open.

State transitions are append-only: any value may supersede any other value via a new revision; the prior revision is retained with its timestamp and `recorded_by`. A terminal disposition may be reopened only by a superseding non-terminal or terminal revision that explicitly references the prior terminal disposition (`reopened_from_ref`).

---

## §4 Workflow Lifecycle

Deterministic five-step loop:

1. **Finding surfaced** — A Delta Tripwire (or future vendor-payment-change) finding is emitted by the detector with its existing `finding_id`, redacted display, signal type, baseline state, and mandatory out-of-band verification wording. The finding's open state is `awaiting_disposition`.
2. **Human verifies out-of-band** — The operator / MSP reviewer contacts the vendor through a previously-known channel per the finding's mandatory wording. This is a human action outside NorthStar.
3. **Disposition recorded** — The reviewer records one of the four §3 values plus the mandatory evidence fields (§5). The record links to `finding_id`.
4. **Linkage resolved** — If non-terminal (`unresolved` / `follow_up_needed`), a follow-up item is created with `prior_disposition_ref`. If `false_positive`, a `correction_loop_ref` is recorded (or marked pending per §10 Q4). If `verified`, the finding's open state closes.
5. **Loop closure / reopen** — A terminal disposition closes the finding; a later revision may reopen it via `reopened_from_ref`. The audit trail records every open / revise / close event so the full history is reconstructible from the trail alone.

A follow-up item that is never dispositioned past its operator-named expiry is drift and surfaces in the digest/report rendering per §7.

---

## §5 Disposition Record & Evidence Schema

### §5.1 Disposition record shape (illustrative; on-disk surface decided in §10 Q3)

```text
disposition_id          string, opaque, unique
tenant_id               string
finding_id              FK to the Delta Tripwire / vendor-payment-change finding
disposition             one of {verified, unresolved, false_positive, follow_up_needed}
verification_channel    one of the §5.2 closed channel values
what_was_confirmed      string, <=280 chars, structured, no chain-of-thought, no raw values
recorded_by             reviewer identifier (operator id or delegated initials per §10 Q5)
recorded_at_utc         ISO-8601 UTC
prior_disposition_ref   nullable; required when this revision supersedes a prior disposition
reopened_from_ref       nullable; required when reopening a terminal disposition
follow_up_item_ref       nullable; required (non-null) when disposition is non-terminal (D6)
correction_loop_ref     nullable; required (non-null) when disposition == false_positive (D7)
supersedes              nullable disposition_id of the revision this one replaces
revision_index          int, monotonically increasing per finding
```

No raw financial string, no PII, no chain-of-thought in any field (D4 / §1.3).

### §5.2 Verification-channel closed enum (v1)

Records *how* the human verified, never the destination itself:

- `previously_known_phone` — called a phone number already on file for the vendor (not from the email).
- `previously_known_email_thread` — confirmed via an established prior email relationship (not a reply to the flagged message).
- `in_person_or_known_contact` — confirmed with a known named contact.
- `vendor_portal_known_login` — confirmed through the vendor's portal using pre-existing credentials (not a link in the email).
- `not_attempted` — disposition recorded without an out-of-band attempt (valid only for `false_positive` or `follow_up_needed`; never for `verified`).

`verified` MUST use one of the first four channels. Using `not_attempted` with `verified` is `not_eligible_for_closure`.

---

## §6 Audit Trail Events

Append-only event stream (on-disk surface decided in §10 Q3). Event types:

```text
disposition_opened        first disposition recorded for a finding
disposition_revised       a superseding revision recorded (carries supersedes + revision_index)
disposition_closed        a terminal disposition closed the finding's open state
disposition_reopened      a revision reopened a previously terminal finding
follow_up_created         a non-terminal disposition spawned a follow-up item
follow_up_expired         a follow-up item passed its operator-named expiry without disposition
```

Each event carries `event_id` (uuid v4), `occurred_at_utc`, `tenant_id`, `finding_id`, `disposition_id`, `actor`, and a `structured_payload` with no raw email content, no raw financial values, no PII, no chain-of-thought. Lint inherits the existing project audit-record discipline.

---

## §7 Rendering Surface (digest / report)

v1 renders disposition state as a digest/report-friendly line, consistent with the Alert-fatigue doctrine (`CURRENT_STATE_MAP.md`): one batched status per tenant, not a per-event alert stream. Illustrative line shapes:

- `Vendor payment change for <vendor display>: VERIFIED via previously-known phone (recorded <date>).`
- `Vendor payment change for <vendor display>: FOLLOW-UP NEEDED — awaiting vendor written confirmation (opened <date>).`
- `Vendor payment change for <vendor display>: marked FALSE POSITIVE — correction recorded.`

Open non-terminal dispositions past their operator-named expiry render as a drift line so they are not silently forgotten. Rendering technology (digest text, JSON, report, eventual portal) is out of scope; metric/line shape only. No forbidden-language phrasing; no payment instruction phrasing.

---

## §8 Relationship to Existing Surfaces

- **Financial State Ledger / Delta Tripwire** (`Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`) — produces the findings this layer dispositions. This spec is the workflow state machine FSL §1 deferred. No FSL decision changes.
- **Two-Channel Confirmation Enforcement** (`Two_Channel_Confirmation_Enforcement_Deep_Dive.md`) — provides the `pending` / `outcome` verification *mechanism* and a binary confirmed/denied outcome. This layer adds the four-value disposition + evidence + retest linkage that a binary outcome does not capture. Whether to reuse, extend, or sit beside the two-channel outcome enum is §10 Q2; v1 does not merge them.
- **Email Security Testing & Evidence Framework** (`Email_Security_Testing_Evidence_Framework_Deep_Dive.md`) — its §9.4 failure-card / §9.5 retest loop is the pattern a `false_positive` disposition links into. This layer records the linkage; it does not duplicate the failure-card schema.
- **Reaction Timing Test Log** (`REACTION_TIMING_TEST_LOG.md`) — its closed verdict enum (`pass` / `partial` / `fail` / `blocked`) is the spiritual sibling of this four-value enum, not a verbatim reuse. Disposition timing, if ever measured, follows the reaction-timing documentation rule (`AGENTS.md` §5).
- **Cyber Insurance Evidence Package** (`Cyber_Insurance_Evidence_Package_Deep_Dive.md` §14) — its Detection -> Verification -> Evidence -> Audit Trail -> Outcome Documentation arc maps cleanly onto this layer's disposition + evidence + audit-trail + rendering. A future implementation could feed dispositions into the package's Outcome Documentation stage under that spec's own §11/§13 contract; no claim is made here.

---

## §9 Failure Modes

- **Disposition-as-authorization** — treating `verified` as authorization to release payment or as operator sign-off. Forbidden by D5 / D8 / §1.3.
- **Silent re-flag amnesia** — a finding re-fires and a reviewer re-chases it because the prior `verified` disposition was not linked. Prevented by D2 one-open-per-finding + append-only history.
- **Buried false positive** — an over-flag dispositioned `false_positive` with no `correction_loop_ref`, so the detector never learns. Prevented by D7.
- **Raw-value leak** — a reviewer pastes the actual new account number into `what_was_confirmed`. Forbidden by D4 / §1.3; enforced at write-time, not convention.
- **Stale follow-up rot** — a `follow_up_needed` disposition left open indefinitely. Surfaced as drift by §7 expiry rendering.
- **Forbidden-language slip** — disposition or rendered text drifts into "compliant" / "insurer-approved" framing. Forbidden by D11.
- **Cross-tenant bleed** — one tenant's disposition history visible to another. Forbidden by D10.

---

## §10 Open Questions

These are operator decisions. The assistant must not pre-decide them. The spec is pre-§11 until they are resolved and Matt signs.

- **Q1. Follow-up expiry / SLA.** Should `unresolved` and `follow_up_needed` carry a default operator-named expiry (echoing the Testing Framework D20 "hard expiry" pattern), and if so what default window? Or is expiry always per-finding operator-set with no default?
- **Q2. Relationship to Two-Channel Confirmation outcome enum.** Reuse the two-channel `outcome_status`, extend it, or keep this four-value enum entirely beside it? This determines whether the two surfaces share storage or stay independent.
- **Q3. On-disk surface.** Where do disposition records and audit events live — a new Blackboard record type, a per-tenant ledger file under `production_state/{tenant_id}/`, or an extension of an existing surface? This drives the isolation + audit-integration design.
- **Q4. `false_positive` correction-loop linkage.** Does a `false_positive` disposition auto-open an Email Security Testing & Evidence Framework failure card (D29-style `decision_audit_candidate_id` linkage), or only record a nullable `correction_loop_ref` the operator populates manually?
- **Q5. Who may record a disposition.** Operator-only, or a delegated MSP reviewer with structured initials (echoing Testing Framework D13 reviewer-note `initials`)? This affects `recorded_by` shape and the audit `actor` field.
- **Q6. Idempotency key.** Is `finding_id` globally unique, or is the open-disposition key the `(tenant_id, finding_id)` pair? (D2 currently assumes the pair; confirm against the FSL finding-id contract.)

---

## §11 Sign-Off Placeholder

**Status:** UNSIGNED. This draft is pre-§11. The decisions in §2 are advisory until Matt signs.

**Locked decisions covered by this signature, once given:** D1–D12 as drafted in §2, the four-value disposition state model in §3, the workflow lifecycle in §4, the record + evidence schema and verification-channel closed enum in §5, the audit-event set in §6, the rendering boundary in §7, and the relationship boundaries in §8. The §10 open questions are NOT covered until each is resolved by operator decision and reflected in §2 / the relevant section.

**Signed by:** ____________________________________

**Date:** ____________________________________

**Signature is incomplete.** Implementation does **not** begin until §11 is signed, every §10 open question is resolved, and a separate explicit operator start-build instruction is issued.
