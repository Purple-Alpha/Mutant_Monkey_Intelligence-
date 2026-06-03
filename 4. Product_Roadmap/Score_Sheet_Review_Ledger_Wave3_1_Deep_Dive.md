# Score Sheet Review Ledger Helper Deep Dive (Wave 3.1)

**Status:** §12 signed 2026-06-03 by Matt Nichol (Zebra-Comit). Governing Wave 3.1 implementation spec. Spec-only; authorizes no runtime code, no hook code, no canonical ledger automation, no operator-state write path, and no client-facing copy until a separate §13 "start build" authorization.

**Date drafted:** 2026-06-03

**Authority:** Matt Nichol. Wave 3 §11 authorizes drafting this Wave 3.1 spec, but this file does not authorize implementation until §12 is operator-signed and Matt separately gives an explicit §13 "start build" instruction.

---

## §0 Purpose

Define the narrow contract for `audit_tools/review_ledger.py` and the coupled no-PII / no-secrets pre-commit scanner.

Wave 3 established that candidate promotion is manual only. Wave 3.1 may reduce operator fatigue and toxic-payload leakage risk, but it must not convert candidate review into automated promotion.

The helper may **read, summarize, scan, prompt, and draft**. It must not promote.

---

## §1 Governing Inputs

This spec inherits and must not weaken:

| Source | Binding rule carried forward |
|---|---|
| `4. Product_Roadmap/Score_Sheet_Candidate_Review_Promotion_Deep_Dive.md` | Manual-only promotion; 8-item checklist; `event_id` assigned at promotion only; `recorded_by` operator-bearing only after operator act; `Testing_Score_Sheet_Schema.md` default write surface; 100-row split trigger; crypto rejected for v1 |
| `think_sheet.md` §14 staging-fatigue addendum | `review_ledger.py` is a critical control candidate against operator fatigue and toxic leakage, not convenience tooling |
| `audit_tools/pre_ship_audit.py` | Existing pre-commit review surface; no secrets printed; local reports only |
| `Internal_Tools/precommit_llm_safety_hook.sh` and `.github/workflows/llm_safety_check.yml` | Existing pattern-mirroring discipline for scanner/hook parity |

If this Wave 3.1 spec conflicts with signed Wave 3, Wave 3 wins.

---

## §2 Scope

### §2.1 In scope

- `audit_tools/review_ledger.py` as an operator-run CLI helper for candidate review.
- Listing unresolved `*.candidate.jsonl` packets under `audit_outputs/score_sheet_candidates/`.
- Parsing packet headers and candidate rows without changing them.
- Displaying the Wave 3 8-item checklist as prompts.
- Running a shared toxic-content scanner over candidate rows and draft outputs.
- Drafting non-canonical promotion-row text for operator review.
- Producing scan findings that point to file, row, field, and reason without echoing sensitive values.
- Defining a coupled pre-commit hook contract that blocks obvious PII / secrets / raw payload leakage in score-sheet evidence surfaces.

### §2.2 Out of scope

- Auto-promotion.
- Writing to `Testing_Score_Sheet_Schema.md`.
- Creating or writing a dedicated canonical ledger file.
- Moving packets to `promoted/` or `rejected/`.
- Deleting candidates.
- Assigning final `event_id`.
- Setting final operator-bearing `recorded_by`.
- Editing `audit_tools/pre_ship_audit.py`, `audit_tools/score_sheet_candidate_emit.py`, emitters, scoring code, detectors, production state, tenant state, or runtime loops.
- Cryptographic signatures, HMACs, external key management, or append-only crypto logs.
- Buyer-facing, underwriter-facing, MSP-facing, compliance, certification, coverage, premium, fraud-prevention, or insurer-approval claims.

---

## §3 Allowed CLI Surface

Wave 3.1 v1 may implement only these commands:

| Command | Purpose | Write behavior |
|---|---|---|
| `list` | Show unresolved candidate packets and basic metadata | Read-only |
| `inspect <packet>` | Print packet header, row count, row summaries, and scan status | Read-only |
| `check <packet>` | Run checklist and toxic-content scanner; print blocking / warning findings | Read-only |
| `draft <packet> --row N` | Emit a non-canonical draft 13-column promotion row to **stdout only** | Read-only (no file writes) |
| `stale` | Report deferred or unresolved packets older than 60 days (operator-confirmed default) | Read-only |

No `promote`, `reject`, `archive`, `move`, `delete`, `write-ledger`, `assign-event-id`, or `draft --out` command is authorized in v1.

### §3.1 Draft output rule

Draft output must be visibly non-canonical:

- `event_id` must be `OPERATOR_TO_ASSIGN`, not a generated `TE-...` value.
- `recorded_by` must be `OPERATOR_TO_SET`, not `operator-Matt`.
- `event_date` may be suggested as `OPERATOR_TO_CONFIRM_YYYY-MM-DD`.
- `notes` may include `candidate_packet_id`, `candidate_ref`, and `archive_pointer_pending`.
- The output must include the marker `DRAFT_NOT_CANONICAL`.

The draft exists to reduce typing burden. It does not become evidence until the operator edits and writes it into the canonical surface by hand.

v1 draft output is **stdout-only**. The operator may redirect stdout manually if desired; the helper must not accept `--out` or write draft files itself.

---

## §4 Shared Scanner Contract

The review helper and pre-commit hook must import one shared Python scanner module. Duplicate scanner logic in separate files is not allowed.

**Operator-confirmed v1 module path:** `audit_tools/score_sheet_review_scanner.py`

That module owns pattern constants, scan entrypoints, finding classes (`BLOCK` / `WARN`), and the no-echo output formatter. `review_ledger.py` and the score-sheet safety hook call into it; they do not re-declare patterns locally.

The scanner must detect at least:

| Class | Examples / intent |
|---|---|
| Secrets | private-key blocks, GitHub tokens, xAI/OpenAI/Anthropic-style API key assignments, bearer-token literals |
| Financial raw data | raw routing numbers, raw account numbers, IBAN-like strings, SWIFT/BIC-like strings, payment-card-like numbers |
| Raw payload leakage | pasted email bodies, raw headers, live URLs with query tokens, unredacted attachment text |
| Real PII markers | real email addresses, real phone numbers, real person names when not already allowed as operator identity |
| Chain-of-thought leakage | `chain_of_thought`, `hidden_reasoning`, or equivalent labels |

Allowed placeholders:

- `redacted`
- `example`
- `test-secret`
- `.example` domains
- fictional tenants already used in repo examples, such as `acme-industries-demo` and `bluefin-marine-supplies-demo`
- explicit synthetic account placeholders, e.g. `ACCOUNT_PLACEHOLDER`, `ROUTING_PLACEHOLDER`, `IBAN_PLACEHOLDER`

### §4.1 Scanner output discipline

Scanner findings must not print the sensitive value. They may print:

- path
- line number or JSONL row index
- field name
- finding class
- short reason
- remediation hint

Example shape:

```text
BLOCK raw_financial_identifier path=audit_outputs/... row=2 field=finding_summary reason=iban_like_string remediation=replace with IBAN_PLACEHOLDER
```

---

## §5 Pre-Commit Hook Contract

The Wave 3.1 hook is a local safety net, not a promotion engine.

It may scan staged files that are likely to become canonical evidence or review artifacts:

- `4. Product_Roadmap/Research_Inputs/Testing_Score_Sheet_Schema.md`
- future dedicated ledger file if the §9.1 100-row split trigger fires
- `PROJECT_ACTIVITY_LOG.md`
- `audit_outputs/score_sheet_candidates/**/*.candidate.jsonl` when intentionally staged
- Wave 3 / Wave 3.1 spec files if they contain examples

It must not scan `.venv`, `.git`, `node_modules`, binary files, local-only `.env`, or gitignored audit reports unless those files are staged.

### §5.1 Blocking behavior

The hook must block on secrets, raw financial identifiers, obvious live credentials, chain-of-thought labels, and raw payload leakage.

The hook may warn, not block, on ambiguous natural-language PII patterns when the finding could be a fictional example. Warnings must still be visible to the operator before commit.

### §5.2 Separate hook (operator-confirmed)

Wave 3.1 v1 ships a **separate** local pre-commit hook beside the existing LLM safety hook. It must not replace or silently extend `Internal_Tools/precommit_llm_safety_hook.sh`.

**Proposed hook path:** `Internal_Tools/precommit_score_sheet_safety_hook.sh`

Install instructions live in `Internal_Tools/README.md` as an additive step. Both hooks may run on the same commit; each keeps its own scope. A future CI mirror, if added, must be a separate workflow file and is out of scope for Wave 3.1 v1 unless operator separately authorizes it.

---

## §6 Review Helper Checklist Flow

For each candidate row selected by the operator, `review_ledger.py check` may display the Wave 3 checklist:

| # | Prompt | Helper behavior |
|---|---|---|
| 1 | Finding is real, not a tool artifact | Show candidate summary and source artifact pointer |
| 2 | `failure_type` is correct | Validate enum/null shape only; operator decides correctness |
| 3 | No PII / secrets / raw payloads | Run scanner and block draft output on scanner BLOCK findings |
| 4 | `track` maps to closed taxonomy | Validate against Wave 0 taxonomy / configured slug map |
| 5 | `finding_summary` is accurate and complete | Prompt operator to edit outside the tool or pass edited text |
| 6 | `corrective_action` / `retest_reference` filled or intentionally blank | Report missing fields; do not invent closure |
| 7 | `event_id` assigned at promotion only | Fail if candidate already carries a canonical `TE-...` value |
| 8 | Operator identity and date recorded | Draft placeholders only; operator writes final canonical values |

The helper must treat checklist answers as review assistance only. It must not persist an operator approval as canonical proof.

---

## §7 Draft Row Shape

`draft` output must follow the Wave 3 13-column promotion contract:

`event_id`, `event_date`, `track`, `event_type`, `source_artifact`, `test_or_check_name`, `pass_fail`, `failure_type`, `finding_summary`, `corrective_action`, `retest_reference`, `recorded_by`, `notes`

Required draft transformations:

- Preserve `track`, `event_type`, `source_artifact`, `test_or_check_name`, `pass_fail`, and `failure_type` from the candidate when valid.
- Copy narrative fields only as draft text; mark them for operator review.
- Add `candidate_packet_id` and `candidate_ref` to `notes` when present.
- Add `DRAFT_NOT_CANONICAL` to `notes`.
- Never infer a pass from a later retest; preserve failure/retest linkage per Wave 3 §7.5.

---

## §8 Deferred / Stale Candidate Reporting

The `stale` command is **in scope for v1** and may flag unresolved or deferred packets older than the Wave 0 carry-forward threshold. The operator-confirmed default threshold is **60 days** unless changed in a signed amendment.

Stale reporting is advisory:

- It may print `STALE_REVIEW_NEEDED`.
- It may sort stale packets to the top.
- It may not reject, delete, archive, or promote stale packets automatically.

---

## §9 Implementation Test Plan

No code may be written until §12 is signed and the operator separately gives §13 "start build." When implementation is authorized, the minimum tests are:

1. `list` ignores `promoted/` and `rejected/` packets and shows unresolved candidates only.
2. `inspect` parses valid JSONL packets and fails closed on malformed packet headers.
3. `check` blocks draft output when scanner BLOCK findings exist.
4. `check` fails when a candidate row already contains a canonical `TE-...` `event_id`.
5. `draft` emits `OPERATOR_TO_ASSIGN`, `OPERATOR_TO_SET`, and `DRAFT_NOT_CANONICAL`.
6. `draft` has no `--out` flag and writes nothing to disk.
7. Scanner does not echo the matched secret / PII / financial value in output.
8. Scanner allows explicit placeholders and `.example` domains.
9. `score_sheet_review_scanner.py` is the only pattern source; helper and hook import it.
10. Separate score-sheet safety hook blocks staged canonical evidence containing a fake secret pattern fixture.
11. Score-sheet safety hook does not scan unstaged or gitignored local-only files.
12. `stale` flags packets older than 60 days as `STALE_REVIEW_NEEDED` without mutating packets.
13. No command moves, deletes, or rewrites candidate packet files.
14. No command imports or calls `pre_ship_audit.py` network/audit execution paths.

---

## §10 Failure Modes

| ID | Failure mode | Detection |
|---|---|---|
| W3.1-1 | Draft becomes promotion | Tool writes canonical surface or omits `DRAFT_NOT_CANONICAL` |
| W3.1-2 | Operator identity laundering | Tool writes `operator-Matt` / `operator-Matt + AI-drafted under operator review` into draft output |
| W3.1-3 | Event-ID laundering | Tool assigns `TE-...` instead of `OPERATOR_TO_ASSIGN` |
| W3.1-4 | Toxic echo | Scanner prints the sensitive value it found |
| W3.1-5 | Hook theater | Hook scans too little or only warns on obvious secrets/raw financials |
| W3.1-6 | Hook overreach | Hook scans local secrets outside staged evidence surfaces and creates noisy false stops |
| W3.1-7 | Archive mutation | Tool moves, deletes, renames, or rewrites candidate packets |
| W3.1-8 | Schema drift | Draft row shape diverges from the Wave 3 13-column contract |

---

## §11 Open Questions Before Signature

1. Should `draft --out` be allowed at all in v1, or should draft output be stdout-only?
2. What exact file should hold the shared scanner patterns: Python module constants, JSON pattern file, or both with parity tests?
3. Should the pre-commit hook be a new separate hook or an extension of the existing LLM safety hook install path?
4. Should the first implementation include `stale`, or defer stale reporting until candidate volume exists?

### §11.A Operator-Confirmed Decisions (2026-06-03, pre-§12)

These resolve the §11 questions as operator-confirmed decisions. They feed the §12 signature but do **not** sign §12 or authorize implementation.

1. **Q1 — Draft output:** **stdout-only in v1.** No `--out`, no helper-written draft files. Operator may redirect stdout manually.
2. **Q2 — Scanner source of truth:** **Single Python module** at `audit_tools/score_sheet_review_scanner.py`, imported by both `review_ledger.py` and the score-sheet safety hook.
3. **Q3 — Hook shape:** **Separate hook** at `Internal_Tools/precommit_score_sheet_safety_hook.sh`, installed beside the existing LLM safety hook without replacing it.
4. **Q4 — Stale reporting:** **Include `stale` in v1** with a read-only 60-day default threshold and `STALE_REVIEW_NEEDED` advisory output only.

### §11.B Implementation Boundary

These decisions are pre-§12. No `review_ledger.py` code, no `score_sheet_review_scanner.py` code, no score-sheet safety hook code, no canonical ledger automation, no emitter changes, and no client/compliance/insurance claims are authorized by this block alone.

---

## §12 Sign-Off

**Matt Nichol (Zebra-Comit) June 3rd. 2026.** Do not infer, draft, or auto-fill.

This §12 signature ratifies this Wave 3.1 spec and its §11.A operator-confirmed decisions as governing truth for the future `review_ledger.py` helper, the shared `score_sheet_review_scanner.py` module, and the separate score-sheet safety hook. It does **not** authorize any implementation: still **no** `review_ledger.py` code, **no** scanner-module code, **no** pre-commit hook code, **no** canonical ledger automation, and **no** change to emitters until a separate explicit operator §13 "start build" authorization.

---

## §13 Start-Build Authorization

**Pending operator authorship.** Do not infer, draft, or auto-fill.

This is intentionally separate from §12. Signing the spec ratifies the contract; it does not start coding.

---

**End of Wave 3.1 draft.**
