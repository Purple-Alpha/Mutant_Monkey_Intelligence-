# Score Sheet Candidate Emit Implementation Deep Dive (Wave 2)

**Status:** Draft pre-spec. Not §11 signed. Not implementation authorization. Not runtime code yet. Not a canonical ledger write path. Not client-facing copy.

**Date drafted:** 2026-06-02

## §0 Purpose

Define exactly how the first candidate emitter would be implemented under the signed Wave 1 candidate-emission contract (`Score_Sheet_Candidate_Emit_Deep_Dive.md`).

This is a Wave 2 implementation specification. It is still a draft. It does not authorize writing code. Code begins only after this spec is §11-signed.

## §1 Scope

In scope: the precise behavior of one emitter, its output, its safety refusals, and a test plan to validate it once authorized.

Out of scope: writing the emitter code, modifying `pre_ship_audit.py`, canonical ledger writes, automatic promotion, interactive review scripts, pre-commit hook implementation, additional emitters, D10, §13, client-facing copy, and any compliance/insurance claim.

## §2 Governing Contract

This spec inherits and must not contradict the signed Wave 1 contract:

- JSONL candidate packets with a `packet_header` first line.
- Multi-track packets allowed; each row carries its own `track`.
- `event_id` is null at emission and assigned only at promotion.
- Filename: `YYYYMMDDTHHMMSSZ_<emitter>_<short_context>.candidate.jsonl`.
- Resolved packets move to `promoted/` or `rejected/` with status suffix; never deleted.
- `recorded_by` = `tool_candidate`.
- Manual-only promotion.
- No-PII / no-secrets / no-raw-payload guard.
- Closed nine-value `track` taxonomy from Wave 0 Q11.

## §3 First Emitter

The first and only Wave 2 emitter is `audit_tools/pre_ship_audit.py`.

It is chosen because it already performs audit checks, is internal, and does not touch client-facing or runtime product behavior.

This spec describes a separate emit path. It does not authorize editing the existing audit logic until §11 is signed.

## §4 When It Emits

The emitter produces a candidate packet when a pre-ship audit run yields recordable outcomes: a check failed, was blocked, produced a partial result, surfaced a false positive or false negative, suggested a corrective action, or produced retest evidence.

A clean run with nothing recordable should not emit an empty packet. No-op runs produce no candidate file.

## §5 Output Location And Filename

Active candidate packets are written under `audit_outputs/score_sheet_candidates/`.

The filename follows the Wave 1 convention with `pre_ship_audit` as the emitter and a short run-context slug.

Resolved packets are later moved by the operator to `promoted/` or `rejected/` subdirectories with a status suffix. The emitter itself never moves or deletes packets.

## §6 File Write Behavior

Each packet is a single `.jsonl` file. The first line is a packet header object. Each following line is one candidate row object.

Writes must be atomic: write to a temporary file in the same directory, then rename into place, so a partial write never leaves a half-written candidate file.

The emitter appends nothing to existing packets. Each run writes a new packet file.


## §7 Field Population Rules

Packet header line carries: `record_type` = `packet_header`, `candidate_packet_id`, `emitter` = `pre_ship_audit.py`, `emitted_at` UTC timestamp, `status` = `AI-drafted`, `promotion_status` = `not_reviewed`, and a `source_run` block describing the command and output reference.

Each candidate row carries: `record_type` = `candidate`, `candidate_ref` = `candidate_packet_id` + row index, `event_id` = null, `event_date`, `track`, `event_type`, `source_artifact`, `test_or_check_name`, `pass_fail`, `failure_type`, `finding_summary`, `corrective_action`, `retest_reference`, `recorded_by` = `tool_candidate`, and `notes`.

The `track` value must come from the closed Wave 0 Q11 taxonomy. If the emitter cannot map a finding to a closed track, it uses a clearly provisional label and the row stays non-promotable until mapped.

## §8 PII / Secrets / Raw-Payload Refusal

Before writing any candidate row, the emitter scans the row content for unsafe material.

Minimum scanner rules:

- Block on probable secrets: API key prefixes, tokens, passwords, authorization headers.
- Block on raw mailbox payloads or full message bodies.
- Block on personal data such as real email addresses or phone numbers that are not fictional `.example` placeholders.

On detecting unsafe content the emitter must either omit the unsafe field and record a redaction note, or emit a blocked/safety candidate that records the refusal without copying the unsafe payload. It must never write the unsafe value into the candidate file.

## §9 Authority Boundaries In Code

The emitter:

- never writes to the canonical ledger
- never assigns `event_id`
- never sets `promotion_status` beyond `not_reviewed`
- never moves a packet into `promoted/`
- never deletes a packet
- never makes a pass/fail claim beyond what the underlying audit check produced

All promotion remains a manual operator act per the signed Wave 1 contract.

## §10 Failure, Correction, And Retest Representation

The emitter preserves the existing loop. It may emit candidate rows for failures, blocked checks, partial results, false positives, false negatives, calibration observations, corrective-action suggestions, and retest evidence.

It must not suppress a failed check because a later retest passed. Both the original failure and any retest evidence should be representable as separate candidate rows.

## §11 Test Plan (For Use Once Authorized)

When implementation is authorized, validation should include:

- a dry-run mode that prints the packet without writing a file
- a fixture run that produces a known failing check and confirms a candidate packet is written with correct fields
- a clean run that confirms no packet is written
- a safety test that feeds unsafe content and confirms refusal/redaction
- a confirmation that `event_id` stays null and no canonical ledger file is touched
- a confirmation that atomic write leaves no partial files on interruption

These tests would themselves become testing-evidence rows once the system is live.

## §12 Sign-Off And Non-Authorizations

Sign-off: unsigned.

No code may be written until this spec is §11-signed.

This spec does not authorize implementation, edits to `pre_ship_audit.py`, canonical ledger writes, automatic promotion, pre-commit hook implementation, interactive review scripts, additional emitters, D10 completion, §13 sign-off, client-facing copy, or any compliance, certification, insurer-approval, coverage, premium, or fraud-prevention claim.
