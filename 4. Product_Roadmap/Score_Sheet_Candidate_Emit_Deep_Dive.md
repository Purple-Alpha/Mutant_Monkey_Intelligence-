# Score Sheet Candidate Emit Deep Dive

**Status:** Draft pre-spec. Not §11 signed. Not implementation authorization. Not runtime code. Not a canonical ledger write path. Not client-facing copy.

**Date drafted:** 2026-06-02

## §0 Purpose

Define the Wave 1 candidate-emission discipline for internal testing evidence rows.

A candidate row is not evidence. A candidate row is an internal draft produced by a tool or AI-assisted process. It may become evidence only after explicit operator review and promotion.

This preserves the existing testing loop: surface failures, record false positives and false negatives, explain corrective actions, preserve retest evidence, and never weaken tests to make failures disappear.

## §1 Scope

In scope: candidate file format, candidate storage location, 13-column mapping, lifecycle, operator-promotion boundary, no-delete rule, no-PII guard, and first emitter candidate.

Out of scope: implementation, canonical ledger writes, pre-commit hook implementation, interactive review script implementation, client-facing reporting, D10 completion, §13 sign-off, compliance, certification, insurer-approval, coverage, premium, or fraud-prevention claims.

## §2 Existing Contract To Preserve

Wave 1 inherits the Wave 0 discipline.

The canonical evidence row schema remains the 13-column schema:

1. `event_id`
2. `event_date`
3. `track`
4. `event_type`
5. `source_artifact`
6. `test_or_check_name`
7. `pass_fail`
8. `failure_type`
9. `finding_summary`
10. `corrective_action`
11. `retest_reference`
12. `recorded_by`
13. `notes`

There is one canonical ledger. Per-track views are filtered views only. Candidate emitters must not create separate per-track ledgers.

## §3 Candidate File Location

Candidate rows must be written under:

`audit_outputs/score_sheet_candidates/`

Files in this directory are internal drafts only. They are not canonical evidence and do not count as proof until reviewed and promoted by the operator.

Recommended initial filename shape:

`YYYYMMDDTHHMMSSZ_<emitter>_<short_context>.candidate.json`

## §4 Candidate File Shape

Candidate packets should identify the packet, emitter, emitted timestamp, source run, review status, and one or more candidate rows mapped to the 13-column schema.

Recommended candidate status values:

- `AI-drafted`
- `not_reviewed`
- `needs_edit`
- `rejected`
- `promoted`
- `archived_after_promotion`

Open question for §11: JSON, JSONL, or YAML.

## §5 Required Candidate Rules

Every candidate row must map to all 13 canonical columns, include `track`, use closed enum values, identify the source artifact or run, be marked candidate / not reviewed, avoid PII / secrets / raw payloads, preserve failures honestly, and remain non-authoritative until promoted.

Candidate rows must not write directly to the canonical ledger, auto-promote themselves, erase failed outcomes, create client-facing copy, or claim D10, §13, §11, compliance, certification, insurer approval, coverage, premium reduction, or fraud prevention.

## §6 Candidate Lifecycle

1. Tool emits candidate packet under `audit_outputs/score_sheet_candidates/`.
2. Candidate remains `AI-drafted` / `not_reviewed`.
3. Operator reviews the packet.
4. Operator rejects, edits, or promotes specific rows.
5. Promoted rows enter the canonical ledger through an operator-controlled path.
6. Original candidate packet is renamed or archived.
7. Candidate packets are never silently deleted.

## §7 Failure, Correction, And Retest Preservation

Candidate emitters must preserve the existing testing loop.

A tool may suggest rows for failed checks, blocked checks, partial results, false positives, false negatives, calibration observations, corrective actions, and retest evidence.

A tool must not hide a failed check because a later retest passed. If a retest passes after correction, the candidate trail should preserve both the original failure or weakness and the correction / retest evidence.

This is not a new testing concept. It is the candidate-emission version of the existing false-positive / false-negative correction evidence loop.

## §8 No-PII / No-Secrets / No-Raw-Payload Guard

Candidate emitters must not write API keys, tokens, passwords, authorization headers, secrets, private customer data, live mailbox payloads, raw proprietary content, or unredacted personal data.

If a source artifact contains unsafe content, the emitter must refuse to emit a candidate packet or emit a blocked/safety candidate that records the refusal without copying the unsafe payload.

## §9 First Emitter Candidate

Recommended first emitter candidate: `audit_tools/pre_ship_audit.py`.

Wave 1 does not authorize modifying `pre_ship_audit.py`. Wave 2 may implement one emitter only after this spec is signed or separately authorized.

## §10 Open Questions For §11

1. Should candidate packets be JSON, JSONL, or YAML?
2. Is `event_id` assigned during candidate emission or promotion?
3. What exact `track` enum values are allowed at Wave 1?
4. What exact `recorded_by` value should tool candidates use?
5. What file naming convention is required?
6. What archive naming convention is required?
7. Should rejected candidates remain forever or move to an archive directory?
8. What minimum PII/secrets scanner runs before candidate write?
9. Can one packet contain multiple tracks?
10. What manual review checklist must the operator complete before promotion?
11. Should promotion be manual copy/edit first, before any review script exists?
12. What proves a candidate was promoted by the operator rather than auto-promoted?

## §11 Sign-Off

Unsigned.

No implementation is authorized until the operator signs this spec or explicitly authorizes a narrower follow-up spec.


## §12 Operator-Confirmed Draft Decisions (2026-06-02, pre-§11)

These resolve the §10 open questions. They are operator-confirmed draft decisions. They are NOT §11-signed and do NOT authorize implementation.

1. **File format (1a):** JSONL. First line is a `packet_header` object; each following line is one `candidate` row.
2. **Multi-track (1b):** A packet may carry candidate rows for multiple tracks. Each row carries its own `track`.
3. **event_id timing (1c):** `event_id` is null at emission and assigned only at promotion. Until then a candidate is tracked by `candidate_ref` = `candidate_packet_id` + row index.
4. **Filename (2a):** `YYYYMMDDTHHMMSSZ_<emitter>_<short_context>.candidate.jsonl`.
5. **Archive handling (2b / 4d):** Resolved packets are moved (never deleted) into `audit_outputs/score_sheet_candidates/promoted/` or `.../rejected/` and given a status suffix (e.g. `.promoted.jsonl`, `.rejected.jsonl`).
6. **Track taxonomy (3a):** The closed `track` taxonomy is deferred to Wave 0 Q11. Candidates may carry a provisional `track` label, but must not be promoted to evidence until the track maps to the resolved Wave 0 taxonomy.
7. **recorded_by (3b):** Tool-emitted candidate rows use `recorded_by` = `tool_candidate`. The specific emitter is recorded in the packet header `emitter` field.
8. **Operator review checklist (4a):** Before promotion the operator confirms: (1) the finding is real, not a tool artifact; (2) failure_type is correct; (3) no PII/secrets/raw payloads; (4) track maps to the resolved taxonomy; (5) finding_summary is accurate and complete; (6) corrective_action and retest_reference are filled or intentionally blank; (7) event_id is assigned at promotion; (8) operator identity and date are recorded.
9. **Promotion mechanism (4b):** Manual only at Wave 1. An automated review/promotion script is deferred to Wave 3.
10. **Proof of operator promotion (4c):** A promoted evidence row carries, in-band, the operator identity, the promotion date, and a back-reference to the originating `candidate_ref` / `candidate_packet_id`.

### §12.1 Still Open For The Implementation Spec

- Exact minimum PII/secrets scanner before candidate write.
- Exact closed `track` taxonomy (inherited from Wave 0 Q11).
- Exact `event_id` assignment format at promotion.

### §12.2 Boundary

Still pre-§11. No implementation, canonical ledger write path, pre-commit hook, review script, D10 completion, §13 sign-off, client-facing copy, compliance, certification, insurer-approval, coverage, premium, or fraud-prevention claim is authorized.
