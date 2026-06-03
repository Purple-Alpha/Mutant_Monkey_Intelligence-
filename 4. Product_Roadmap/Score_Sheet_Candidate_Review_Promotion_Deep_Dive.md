# Score Sheet Candidate Review And Promotion Deep Dive (Wave 3)

**Status:** Draft pre-spec. Not §11 signed. Not implementation authorization. Not runtime code. Not a canonical ledger write path. Not client-facing copy.

**Date drafted:** 2026-06-03

**Authority:** Matt Nichol. Pre-§11 changes flow operator → spec edit → next gate. No implementation, D10, §13, client-facing copy, compliance, certification, insurer-approval, coverage, premium, or fraud-prevention authorization is granted by this draft.

---

## §0 Purpose

Define the Wave 3 human-in-the-loop discipline for reviewing candidate packets emitted under the signed Wave 1 contract and the implemented Wave 2 emitter path (`audit_tools/pre_ship_audit.py` via `audit_tools/score_sheet_candidate_emit.py`).

Wave 2 answers **how tools emit candidates**. Wave 3 answers **how an operator reviews, rejects, defers, or promotes** those candidates into canonical testing-evidence rows without any tool auto-promoting.

This preserves the existing testing loop: surface failures honestly, preserve false-positive / false-negative correction trails, require operator closure, and never weaken tests to make failures disappear.

---

## §1 Scope

### §1.1 In scope

- Candidate holding area semantics for active, deferred, promoted, and rejected packets.
- Enforcement of the existing 8-item operator checklist as a promotion precondition.
- Safe archival of rejected and deferred candidates (no silent deletion).
- The candidate → canonical evidence boundary crossing.
- In-band proof of operator promotion (`recorded_by`, promotion date, `event_id`, back-reference to `candidate_ref` / `candidate_packet_id`).
- What tools are strictly forbidden from doing automatically (the #1 non-negotiable).
- A future review-helper script contract shape only as §10 open questions — **not** implementation authorization.

### §1.2 Out of scope

- Implementation of `audit_tools/review_ledger.py` or any interactive review script.
- Implementation of a no-PII / no-secrets pre-commit hook (bundled with future review-script work per Wave 0 §10.C).
- Modification of `audit_tools/pre_ship_audit.py` or `audit_tools/score_sheet_candidate_emit.py`.
- Additional emitters beyond the signed Wave 2 scope.
- Canonical ledger file creation unless operator separately authorizes promotion to a dedicated ledger file (Wave 0 §10.A Q1).
- Client-facing, buyer-facing, underwriter-facing, or MSP-facing rendering.
- D10 (Cyber Insurance Evidence Package) advance, §13 sign-off, or compliance / insurance claims.
- Adoption of external research artifacts as repo truth (see §2).

---

## §2 External Context Reviewed — Not Adopted As Repo Truth

During Wave 3 planning, operator-supplied Manus conceptual research was reviewed strictly as background context. It is **not** part of the NorthStar repository state and **must not** be cited as implemented, existing, or authorized.

### §2.1 What was reviewed (context only)

- A markdown framework describing anonymized email-pattern test data and compliance guardrails.
- A JSON dataset (`invoice_fraud.json`) with placeholder-driven normal and fraud-labeled records.

Useful **conceptual** signals from that context:

- Placeholder-driven, defanged test data boundaries (no live URLs, synthetic financials, zero real PII).
- Separating benign baseline cases from adversarial fraud-pattern cases for false-positive guardrail thinking.
- Human review before any pattern or row becomes authoritative.

### §2.2 Explicitly not adopted (hallucinated or out of scope for Wave 3 v1)

The following Manus concepts are **rejected for Wave 3 v1** unless a future operator-signed spec adds them:

| Manus concept | Wave 3 disposition |
|---|---|
| `live_test_framework.py` | Does not exist; not referenced as repo surface |
| Enron baseline file tree / `/tests/3_evolutionary_sandbox/` | Does not exist; not referenced as repo layout |
| RICE matrix / North Star Metric / WAU fraud-interception metrics | Product-growth framing; not testing-evidence ledger contract |
| Production filters / tenant stack / active protection deployment | Runtime product scope; forbidden in candidate/promotion path |
| Cryptographic operator signatures / `operator_cli_key_*` | Not Wave 1 in-band proof model; deferred unless operator amends |
| Encrypted candidate packets | Not required; Wave 1 JSONL plain internal drafts under gitignored `audit_outputs/` |
| Immutable Blackboard ledger / append-only crypto event blocks | Different surface; not canonical score-sheet ledger |
| Mutation engine negative-training feedback loop | Phase 1.4 / sandbox scope; not Wave 3 promotion discipline |
| Auto-promotion on operator approval UI | **Forbidden** — conflicts with §8 |

### §2.3 Optional future intake (not Wave 3)

Sanitized external datasets may later enter the repo only through `research_intake` track rows and a separate operator-authorized intake spec. Wave 3 does not import `invoice_fraud.json` or any Manus file into the candidate or evidence paths.

---

## §3 Governing Contracts (Must Not Contradict)

Wave 3 inherits and must not weaken:

| Source | Binding rules carried forward |
|---|---|
| [`Internal_Testing_Evidence_Discipline_Deep_Dive.md`](Internal_Testing_Evidence_Discipline_Deep_Dive.md) | Single canonical ledger; candidate lifecycle; §8 failure modes; §9 audit requirements; nine-value `track` taxonomy (§12) |
| [`Score_Sheet_Candidate_Emit_Deep_Dive.md`](Score_Sheet_Candidate_Emit_Deep_Dive.md) (§11 signed) | JSONL packets; `event_id` null at emission; manual-only promotion; 8-item checklist; `promoted/` / `rejected/` archives; `recorded_by = tool_candidate` |
| [`Score_Sheet_Candidate_Emit_Implementation_Deep_Dive.md`](Score_Sheet_Candidate_Emit_Implementation_Deep_Dive.md) (§11 signed + §14 amendment) | Emitter identity `pre_ship_audit.py`; scanner minimums; promotion-time `event_id` format recommendation |

---

## §4 Candidate Holding Area (Before Review)

### §4.1 Active candidate pool

New candidate packets emitted by Wave 2 land under:

`audit_outputs/score_sheet_candidates/`

This directory is the **holding pit** for unreviewed work. Packets here are internal drafts only. They are not canonical evidence.

Active packets remain in the pool root until the operator resolves them. Filename shape remains per Wave 1:

`YYYYMMDDTHHMMSSZ_<emitter>_<short_context>.candidate.jsonl`

### §4.2 Packet state at arrival

Each arriving packet must satisfy Wave 1 / Wave 2 contracts:

- First line: `packet_header` with `status = AI-drafted`, `promotion_status = not_reviewed`.
- Candidate rows: `event_id = null`, `recorded_by = tool_candidate`.
- `track` must map to the closed nine-value taxonomy or remain explicitly non-promotable with a provisional label.

The holding area does **not** execute packets, deploy rules, or touch production/runtime surfaces.

### §4.3 Operator review queue (manual v1)

Wave 3 v1 has **no automated queue sorter**. The operator review queue is the set of `*.candidate.jsonl` files in the holding pool that still carry `promotion_status = not_reviewed`.

Recommended operator practice (non-binding workflow, not tool behavior):

1. List active candidate files by `emitted_at` (newest or oldest first — operator choice).
2. Open one packet at a time.
3. Complete the §5 checklist before any promotion or rejection.
4. Resolve the packet by move-to-archive per §6 or §7.

A future Wave 3.1 implementation may add `audit_tools/review_ledger.py` only after this spec is §11-signed and a separate build authorization is given.

---

## §5 Operator Checklist (Promotion Precondition)

Before any candidate row is promoted to canonical evidence, the operator must confirm all eight items from the signed Wave 1 §12 checklist. Wave 3 elevates this from emit-spec guidance to a **hard promotion gate**.

| # | Checklist item | Promotion gate rule |
|---|---|---|
| 1 | Finding is real, not a tool artifact | Operator records explicit confirmation in promotion record; reject if artifact-only |
| 2 | `failure_type` is correct | Must be legal enum or null per row rules |
| 3 | No PII / secrets / raw payloads | Re-read row text; refuse promotion if §9.1 guard fails |
| 4 | `track` maps to closed taxonomy | Must be one of nine Wave 0 §12 values; no `misc` / catch-all |
| 5 | `finding_summary` is accurate and complete | Operator may edit before promotion; AI text is not closure |
| 6 | `corrective_action` and `retest_reference` filled or intentionally blank | Explicit blank is allowed; silent omission is not |
| 7 | `event_id` assigned at promotion only | Emitter must not have pre-assigned ID |
| 8 | Operator identity and date recorded | Required in-band proof per §8 |

If any item fails, the operator must **reject** or **defer** — not promote.

### §5.1 Deferral without rejection

A packet may remain in the active pool with `promotion_status = needs_edit` if the operator intends to re-review after correction. Deferral is not promotion. Deferred packets must not write to the canonical ledger.

---

## §6 Rejected And Deferred Candidates (Safe Archive)

### §6.1 Rejection path

When the operator rejects a packet or specific rows:

1. Move the packet file to `audit_outputs/score_sheet_candidates/rejected/`.
2. Rename with status suffix per Wave 1 (e.g. `.rejected.jsonl`).
3. Update packet header `promotion_status` to `rejected` (operator edit on archive copy).
4. Record an operator-authored **rejection reason** in the packet header or in a companion note field — plain English, ≤ 280 characters, no PII/secrets/raw payloads.

Rejected candidates are **never** canonical evidence. They remain available for audit reconstruction.

### §6.2 Rejection reason vocabulary (v1)

Wave 3 v1 does **not** introduce a closed rejection-reason enum. Allowed free-text reasons include:

- `tool_artifact`
- `wrong_failure_type`
- `track_not_mapped`
- `pii_or_secret_risk`
- `duplicate_of_existing_evidence`
- `insufficient_finding_summary`
- `superseded_by_later_run`

A closed enum is §10 carry-forward if row volume justifies it.

### §6.3 Negative training data

Wave 3 v1 does **not** feed rejections into a mutation engine or automated "do not generate again" loop. Rejected archives exist for human audit and optional future specs only.

### §6.4 Silent deletion forbidden

Deleting a candidate packet without archiving to `rejected/` or `promoted/` is a Wave 0 §8.12 / §8.14 failure mode. Tools must not delete packets. Operators must not delete packets without an explicit operator-authored close decision recorded in `PROJECT_ACTIVITY_LOG.md` when exceptional hygiene is required.

---

## §7 Accepted Candidates → Canonical Evidence Rows

### §7.1 Promotion is manual only

Promotion is an **explicit operator act**. No LLM, audit runner, emitter, or background job may promote.

Permitted v1 promotion mechanism:

- Operator reads the candidate packet.
- Operator authors or edits the evidence fields (especially `finding_summary`, `corrective_action`, `why`-equivalent narrative fields).
- Operator writes the row into the canonical evidence surface (see §9).
- Operator archives the source packet to `promoted/`.

Automated copy-from-candidate without operator edit is **not** authorized in v1.

### §7.2 `event_id` assignment at promotion

At promotion time only, assign:

`TE-YYYYMMDD-<track_slug>-NNNN`

Example: `TE-20260603-audit_gate-0001`

Rules:

- `track_slug` is a stable lowercase slug derived from the closed `track` value (operator documents mapping once in promotion practice).
- `NNNN` is a zero-padded sequence per track per UTC day (operator-maintained in v1; tooling may assist only after §11-signed implementation).
- The emitter never assigns `event_id`. Wave 2 §13.3 stands.

### §7.3 `recorded_by` at promotion

Promoted rows must use an operator-bearing value:

- `operator-Matt`, or
- `operator-Matt + AI-drafted under operator review`

Bare `AI-drafted` or `tool_candidate` on a canonical row is a §8 authority-drift failure.

### §7.4 Row mapping (13-column contract)

Promoted rows use the canonical 13-column contract from Wave 1 §2:

`event_id`, `event_date`, `track`, `event_type`, `source_artifact`, `test_or_check_name`, `pass_fail`, `failure_type`, `finding_summary`, `corrective_action`, `retest_reference`, `recorded_by`, `notes`

Candidate field names map directly; operator may refine text during promotion.

### §7.5 Preserve failure and retest trails

Promotion must not collapse a failure away because a later retest passed. If both matter, promote separate evidence rows or one row with explicit `retest_reference` linking the follow-up proof.

---

## §8 In-Band Proof Of Promotion

Every promoted evidence row must carry, **in the row itself** (not only in chat or memory):

| Proof field | Requirement |
|---|---|
| `event_id` | Assigned at promotion per §7.2 |
| `recorded_by` | Operator-bearing value per §7.3 |
| `event_date` | UTC date of promotion decision |
| `notes` or dedicated promotion block | Must include `candidate_packet_id` and `candidate_ref` (packet id + row index) |
| Archive pointer | Path or filename of the promoted packet under `audit_outputs/score_sheet_candidates/promoted/` |

Recommended `notes` shape (non-normative example):

```text
promoted_from: CAND-20260603T120000Z_pre_ship_audit_fix-first.candidate.jsonl#2
promoted_by: Matt Nichol
promoted_at: 2026-06-03T12:05:00Z
```

Cryptographic signatures, HMAC blocks, and external signature keys are **out of scope** for Wave 3 v1. In-band textual proof matches Wave 1 §12 item 10.

---

## §9 Canonical Ledger Surface (While Schema-Only)

Wave 0 §10.A Q1 remains in force: the canonical ledger may stay **schema-only** with rows recorded as repo-resident artifact references and per-event linkage in `PROJECT_ACTIVITY_LOG.md`.

Wave 3 v1 promotion therefore means:

1. The promoted 13-column row is written to the **operator-confirmed default canonical surface: an amendment block in [`Testing_Score_Sheet_Schema.md`](Research_Inputs/Testing_Score_Sheet_Schema.md)** (resolves §10 Q2). Rows live next to the schema that defines them.
2. The source candidate packet is archived under `promoted/`.
3. No separate per-track ledger files are created.

### §9.1 Hundred-row split trigger (operator-confirmed)

The schema-file amendment block is the canonical surface **only while small**. The moment the promoted-row count in that block **crosses 100 rows**, the rows must be split out into a single dedicated ledger file (the option-(c) stub) at the next promotion, and `Testing_Score_Sheet_Schema.md` retains only a pointer to it. This is a mandatory transition, not optional: Markdown row tables degrade past ~100 rows. The split preserves the single-canonical-ledger rule (still one surface, no per-track files) and requires no fresh operator authorization once this threshold is crossed — the threshold itself is the authorization. Crossing 100 rows without splitting is a Wave 3 housekeeping failure.

---

## §10 Open Questions For §11

1. **Review helper script:** Should Wave 3.1 authorize `audit_tools/review_ledger.py` to list packets, display checklist prompts, and draft promotion rows — while still forbidding auto-promotion?
2. **Canonical write surface:** Which single v1 file is the default promotion target while the ledger remains schema-only?
3. **Rejection enum:** When should rejection reasons become a closed enum?
4. **Track slug table:** Should `TE-...-<track_slug>-...` slugs be normatively defined in this spec or in Wave 0?
5. **Deferred packet TTL:** Should deferred candidates auto-flag as stale after N days (Wave 0 Q3 carry-forward)?
6. **Manus dataset intake:** Should sanitized external datasets get a separate `research_intake` spec, wholly outside Wave 3?
7. **Crypto proof:** Explicitly reject for v1, or defer to a future amendment?
8. **Pre-commit hook coupling:** Confirm PII hook ships only with review-script spec, not Wave 3 promotion rules alone.

### §10.A Operator-Confirmed Decisions (2026-06-03, pre-§11)

These resolve the §10 questions as operator-confirmed decisions. They are operator-confirmed and feed the §11 signature, but this block itself does NOT sign §11 or authorize implementation.

1. **Q1 — Review helper:** YES. `audit_tools/review_ledger.py` is authorized as a future **Wave 3.1 spec** (not code) that may list packets, prompt the 8-item checklist, and draft promotion rows. It must never auto-promote, assign canonical `event_id`, set operator-bearing `recorded_by`, move packets to `promoted/`, delete candidates, or write the canonical ledger.
2. **Q2 — Canonical write surface:** `Testing_Score_Sheet_Schema.md` amendment block is the v1 default, subject to the **§9.1 hundred-row split trigger** (auto-split to a dedicated ledger file once the block crosses 100 rows).
3. **Q3 — Rejection enum:** Free-text rejection reasons in v1; revisit a closed enum only when row volume justifies it.
4. **Q4 — Track-slug table:** Defined in **Wave 0** alongside the nine-value `track` taxonomy (Wave 0 §12), not duplicated here. Wave 3 references it.
5. **Q5 — Deferred packet TTL:** Carry forward Wave 0 Q3 (60-day idea) as not-locked; revisit with the Wave 3.1 review helper. No TTL enforcement tooling in Wave 3 v1.
6. **Q6 — Manus dataset intake:** Any sanitized external dataset enters only through a separate operator-authorized `research_intake` spec, wholly outside Wave 3.
7. **Q7 — Crypto proof:** **Explicitly rejected for v1.** In-band textual proof (operator identity + date + `candidate_ref` / `candidate_packet_id`) is the only required proof. A future amendment may revisit if an external party ever requires cryptographic proof.
8. **Q8 — Pre-commit hook coupling:** The no-PII / no-secrets pre-commit hook ships **bundled with the Wave 3.1 review-script spec**, sharing its scanner contract — not with the Wave 3 promotion rules alone.

### §10.B Boundary

Still pre-§11. No implementation, no `review_ledger.py` code, no pre-commit hook code, no canonical ledger automation, no D10 completion, no §13 sign-off, no client-facing copy, and no compliance / certification / insurer-approval / coverage / premium / fraud-prevention claim is authorized by these decisions.

---

## §11 Sign-Off

**Matt Nichol(Zebra-Comit) June, 3rd. 2026.** Do not infer, draft, or auto-fill.

This §11 signature ratifies the spec and its §10.A decisions as governing Wave 3 truth and authorizes the *future drafting* of a Wave 3.1 `review_ledger.py` + PII-hook spec. It does **not** authorize any implementation: still **no** `review_ledger.py` code, **no** pre-commit hook code, **no** canonical ledger automation, and **no** change to emitters until a separate explicit operator "start build" authorization.

---

## §12 Named Failure Modes (Wave 3 Additions)

Recognize and stop by name (extends Wave 0 §8):

| ID | Failure mode | Detection |
|---|---|---|
| W3-1 | **Checklist skipping** | Promoted row without all eight checklist attestations |
| W3-2 | **Promotion without archive** | Canonical row exists but `promoted/` copy missing |
| W3-3 | **Proof-free promotion** | Row lacks `candidate_packet_id` / `candidate_ref` back-pointer |
| W3-4 | **Tool-assisted laundering** | Script writes operator-bearing `recorded_by` without operator act |
| W3-5 | **Rejection without reason** | Archived to `rejected/` but no operator rejection note |
| W3-6 | **Manus fiction import** | Spec, tracker, or row cites non-existent repo files as implemented |

---

## §13 Recommended Cadence After §11

| Step | Action | Authority |
|---|---|---|
| 1 | Operator §11-signs this deep-dive | Matt |
| 2 | 7-axis stress test recorded in `think_sheet.md` | Operator review |
| 3 | Optional: draft `review_ledger.py` implementation spec (Wave 3.1) | Separate §11 |
| 4 | Implement review helper + PII hook only when explicitly authorized | Operator "start build" |

Wave 3 does not authorize step 3 or 4 until step 1 completes.
