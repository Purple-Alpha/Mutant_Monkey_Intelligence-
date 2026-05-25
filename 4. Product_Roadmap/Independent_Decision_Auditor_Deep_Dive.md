# Independent Decision Auditor — Implementation Spec (Deep Dive)

**Status:** §11 SIGNED 2026-05-24 by Matt Nichol; implementation landed 2026-05-24; runtime verification 688 passed, 1 skipped; first self-audit returned `proceed`.  
**Authors:** Matt (operator decisions) + AI scribe (capture).  
**Last reviewed:** 2026-05-24 UTC.  
**Source-of-truth links:** `think_sheet.md` (Independent decision-auditor lane promote row), `audit_tools/grok_audit_runner.py` (independent code-auditor precedent), `PROJECT_GUARDRAILS.md` (Guardrails 8-12), `PROJECT_HANDSHAKE.md` (current build state), `PROGRESS.md` (completed build receipts).

This document is the specification contract for the Independent Decision Auditor workflow. No implementation lands until the §11 Lockdown Signature is filled in by the operator. Once signed, every implementation receipt must cite this file by section number.

---

## §0 Purpose

The Independent Decision Auditor prevents strategic and architectural drift before it becomes code.

The core concern is not lack of trust. Matt trusts the primary assistant, and the project has already benefited from strong recommendations. The risk is subtler:

> A confident primary assistant can shape build order, scope, and architecture before drift becomes visible to the operator.

The Independent Decision Auditor creates a second-model review lane for major decisions. It asks a separate AI to challenge the recommendation, its assumptions, the rejected alternatives, and the timing against the current project state.

The desired output is not a debate transcript and not a replacement for Matt's authority. It is a concise decision-quality report:

1. Is the recommendation sound?
2. What bias, blind spot, or missing angle may be present?
3. Should the decision proceed, be revised, be deferred, or be escalated back to Matt?
4. What exact condition would make the recommendation safer?

This is the governance sibling of the Grok code auditor. The code auditor asks, "Did the build match the signed spec?" The Decision Auditor asks, "Should this build/spec/order be accepted before we commit to it?"

---

## §1 Scope

### In scope (v1)

- A local decision-audit runner under `audit_tools/decision_audit_runner.py`.
- A locked decision-auditor prompt with a stable output schema.
- A Markdown decision packet format that can be produced by the primary assistant before major decisions.
- A local `decision_audit_inputs/` folder for operator-reviewed decision packets.
- Audit outputs written under `audit_outputs/decision_audits/` (gitignored by existing `audit_outputs/` rule).
- A closed verdict enum:
  - `proceed`
  - `proceed_with_notes`
  - `revise_before_proceeding`
  - `defer`
  - `operator_decision_required`
- Required audit sections:
  - Recommendation clarity
  - Fit to current project state
  - Rejected alternatives / missing options
  - Drift or bias risk
  - Cost / timing / opportunity cost
  - Verdict
- Trigger rules defining when a decision audit is required.
- Gate tests proving prompt lock, packet assembly, verdict parsing, no secret inclusion, output path confinement, and fail-closed behaviour on reject/defer verdicts.

### Out of scope (v1)

- No automatic decision-making. The auditor cannot approve work on Matt's behalf.
- No automatic implementation after an audit verdict.
- No direct modifications to runtime, production state, operator state, Git, GitHub, or trackers.
- No network calls from runtime code. The runner lives in `audit_tools/` only, like `grok_audit_runner.py`.
- No raw client data, inbox samples, `.env`, API keys, or private audit outputs included in packets.
- No mandatory audit for tiny local coding choices, typo fixes, test fixes, tracker updates, or implementation details already locked by a signed spec.
- No multi-model voting system in v1. One independent model is enough for the first lane.
- No storage in Blackboard or production state. Decision reports are local artifacts only.

---

## §2 Locked Architectural Decisions

| # | Decision | Locked Value | Rationale |
|---|---|---|---|
| D1 | Runtime boundary | Decision Auditor lives under `audit_tools/`, not `core/` | It makes third-party model calls and is governance tooling, not product runtime. |
| D2 | Runner file | `audit_tools/decision_audit_runner.py` | Keeps it parallel to `grok_audit_runner.py` while separating code audits from decision audits. |
| D3 | Input packet folder | `decision_audit_inputs/` at workspace root | Decision packets should be explicit, reviewable, and never assembled silently from arbitrary files. |
| D4 | Output folder | `audit_outputs/decision_audits/` | Already covered by root `audit_outputs/` gitignore. Reports are local by default. |
| D5 | API key handling | Reuse `.env` `XAI_API_KEY` and optional `XAI_MODEL`; never print, persist, or include the key | Same secret boundary as the code-audit runner. |
| D6 | Default model | `grok-4` unless `XAI_MODEL` overrides | Keeps the independent lane consistent with the current code-audit runner. |
| D7 | Prompt lock | One `DECISION_AUDITOR_PROMPT` constant; edits require spec revision or tracker receipt | Prompt drift undermines repeatability. |
| D8 | Required input shape | One Markdown packet with six sections: decision, recommendation, rationale, alternatives, constraints, current state | The auditor should inspect the decision quality, not reconstruct context from a vague chat excerpt. |
| D9 | Verdict enum | `proceed`, `proceed_with_notes`, `revise_before_proceeding`, `defer`, `operator_decision_required` | More useful than approve/reject for strategic choices. |
| D10 | Fail-closed gate | `revise_before_proceeding`, `defer`, and `operator_decision_required` block implementation until Matt explicitly resolves the audit | Prevents the primary assistant from hand-waving away an independent objection. |
| D11 | Proceed gate | `proceed` and `proceed_with_notes` allow the recommendation to be accepted, but still require Matt's normal explicit command (`lock §11`, `start build`, commit, push, etc.) | The auditor never acts for the operator. |
| D12 | Required audit triggers | New build-lane selection, new §11 spec lock, new subsystem, change to Guardrails 8-12, data-egress boundary decision, persistent-state surface decision, or gold-plating vs necessary-quality dispute | These are the points where drift becomes expensive. |
| D13 | Non-triggered work | Small bug fixes, test fixes, typo edits, tracker receipts, and implementation choices already inside a signed spec do not require a decision audit | Keeps the lane lightweight and usable. |
| D14 | Data minimization | Packets include summaries and file references, not raw secrets, `.env`, raw client emails, or raw financial strings | Governance review should not create a data leak. |
| D15 | Operator authority | Matt can override any verdict, but the override must be written into the packet/result receipt with the reason | Human authority stays explicit and auditable. |
| D16 | Tracker integration | Decision-audit reports for major build-order decisions are cited in `PROJECT_ACTIVITY_LOG.md` and `PROJECT_HANDSHAKE.md` when they affect current direction | Prevents audit results from becoming invisible local artifacts. |

Changing any locked decision requires reopening this spec, not a code-level workaround.

---

## §3 Decision Packet Contract

Each decision packet is one Markdown file in `decision_audit_inputs/`.

File naming:

```text
YYYYMMDD_HHMM_<short_slug>.md
```

Required sections:

```markdown
# Decision Audit Packet — <short title>

## 1. Decision Under Review
<one paragraph naming the decision>

## 2. Primary Recommendation
<the recommendation the primary assistant/operator is leaning toward>

## 3. Rationale Given
<why the recommendation was made>

## 4. Rejected Alternatives
<alternatives considered and why they were rejected or deferred>

## 5. Current Project State
<short state summary with file references; no raw secrets or client data>

## 6. Constraints / Guardrails
<relevant guardrails, timing pressure, budget, risk, tests, user preference>
```

Optional sections:

- `## 7. Operator Concern`
- `## 8. What Would Change My Mind`
- `## 9. Deadline / Urgency`

The runner validates that all six required section headings are present before making any network call.

---

## §4 Auditor Prompt and Output Contract

The runner sends:

1. The locked `DECISION_AUDITOR_PROMPT`.
2. The exact operator-reviewed decision packet.

The model must return exactly these sections:

```text
A. Recommendation clarity
B. Fit to current project state
C. Missing alternatives or assumptions
D. Drift / bias risk
E. Cost, timing, and opportunity cost
F. Verdict
```

The verdict section must contain exactly one machine-readable line:

```text
VERDICT: proceed | proceed_with_notes | revise_before_proceeding | defer | operator_decision_required
```

Then one plain-English paragraph explaining the verdict.

The prompt must explicitly tell the auditor:

- Do not propose unrelated features.
- Do not judge by novelty or excitement.
- Prefer the smallest action that protects the current project direction.
- Flag if the packet lacks enough context.
- Treat Matt's stated constraints as first-class inputs.
- Do not override signed specs unless the decision under review is itself a spec revision.

---

## §5 Trigger Rules

### Audit required

A decision audit is required before accepting the recommendation when any of these are true:

1. Selecting the next major build lane after a completed milestone.
2. Locking a new §11 spec that opens a new subsystem or persistent surface.
3. Changing Guardrails 8-12.
4. Choosing between "defer" and "build now" when the decision affects more than one module.
5. Deciding whether a recommendation is necessary quality or gold-plating.
6. Adding a new data-egress path, external model/API call, or third-party dependency.
7. Adding a new tenant-state, operator-state, production-state, or cross-tenant data surface.
8. Reversing a prior promoted/deferred roadmap decision.
9. Making a pricing/package decision that changes runtime behaviour.
10. Any time Matt explicitly asks for an anti-drift check.

### Audit optional

An audit is optional when:

- The decision is already inside a signed spec's implementation envelope.
- The change is a local bug fix or test hardening.
- The change updates trackers to reflect work already completed.
- The decision is exploratory and no implementation/spec/commit follows from it.

### Audit not allowed

A decision audit must not send:

- `.env` or secrets.
- Raw client emails or attachments.
- Raw financial strings.
- GitHub tokens, API keys, or credential traces.
- `audit_outputs/` contents unless Matt explicitly selects a report for review.

---

## §6 API / CLI Contract

### Module: `audit_tools/decision_audit_runner.py`

Public functions:

```python
def load_xai_key(env_path: Path) -> tuple[str, str]:
    """Load XAI_API_KEY and optional XAI_MODEL from .env without printing secrets."""


def validate_decision_packet(text: str) -> None:
    """Raise SystemExit if any required section is missing or forbidden content appears."""


def extract_verdict(report: str) -> str:
    """Return the machine-readable verdict from the report; raise SystemExit on invalid/missing verdict."""


def call_grok(*, api_key: str, model: str, prompt: str, decision_packet: str) -> str:
    """Call xAI chat completions with the locked decision-auditor prompt."""


def write_decision_audit_report(*, packet_path: Path, model: str, content: str) -> Path:
    """Write report under audit_outputs/decision_audits/."""
```

CLI:

```text
python audit_tools/decision_audit_runner.py decision_audit_inputs/<packet>.md
```

Exit behaviour:

| Condition | Exit |
|---|---:|
| Missing packet | non-zero |
| Missing required section | non-zero before network call |
| Forbidden content pattern detected | non-zero before network call |
| Unknown verdict | non-zero after report write |
| `proceed` / `proceed_with_notes` | zero |
| `revise_before_proceeding` / `defer` / `operator_decision_required` | non-zero unless `--report-only` is passed |

The non-zero exit is intentional fail-closed behaviour for automation.

---

## §7 Gate Tests

Implementation must pass all tests below before §4 can be claimed closed.

1. **Prompt lock.** `DECISION_AUDITOR_PROMPT` contains all six required output headings and the exact `VERDICT:` line contract.
2. **Required section validation.** A packet missing any of the six required headings fails before any network call.
3. **Valid packet accepted.** A packet with all six required headings passes validation.
4. **Forbidden `.env` content blocked.** Packets containing `XAI_API_KEY`, `BEGIN PRIVATE KEY`, `gho_`, or `YOUR_GITHUB_PAT_HERE` fail before network call.
5. **Raw financial pattern blocked.** Obvious raw routing/account strings in a packet fail unless replaced with redacted placeholders.
6. **Output path confinement.** Reports always write under `audit_outputs/decision_audits/`; path traversal in packet name cannot escape.
7. **Verdict parser accepts closed enum only.** The five locked verdicts parse; any other string fails.
8. **Fail-closed verdicts exit non-zero.** `revise_before_proceeding`, `defer`, and `operator_decision_required` return a blocking exit code unless `--report-only` is passed.
9. **Proceed verdicts exit zero.** `proceed` and `proceed_with_notes` return success.
10. **Report-only override.** `--report-only` writes the report and returns zero even for blocking verdicts, but prints the blocking verdict clearly.
11. **No secret echo.** Tests patch `call_grok` and assert the API key never appears in stdout, stderr, report body, or exception text.
12. **No runtime import.** No `core/` runtime module imports `decision_audit_runner.py`; the tool stays outside product runtime.
13. **No Blackboard write.** The runner does not call orchestrator route functions, production state writers, or operator state writers.
14. **Tracker receipt anchor.** `PROGRESS.md` and `PROJECT_ACTIVITY_LOG.md` can be cited by file path in packets, but the runner does not mutate them.
15. **Windows path support.** Packet paths with spaces in the workspace root work on Windows.
16. **Unknown model fallback.** Missing `XAI_MODEL` falls back to `grok-4`.
17. **HTTP error redaction.** xAI HTTP errors do not print authorization headers or the API key.
18. **Decision packet template.** A template file `decision_audit_inputs/TEMPLATE.md` exists with the six required sections and no secrets.
19. **Grok audit runner unaffected.** Existing `grok_audit_runner.py` tests/targets still import and assemble packages.
20. **Spec status gate.** The implementation receipt cannot mark the Decision Auditor lane closed until one self-audit packet has been run against the "Decision Auditor next" build-order choice.

If any test in this list does not pass, the implementation receipt is not allowed to claim §4 closed.

---

## §8 Boundaries & Safety

| Concern | Enforcement |
|---|---|
| Runtime perimeter | Tool lives in `audit_tools/`; no `core/` imports it. |
| Secrets | `.env` read only for `XAI_API_KEY`; key never printed or persisted. Packet validation blocks common secret markers. |
| Client data | Packets use summaries and references only. Raw client emails, raw financial strings, and attachments are forbidden. |
| Operator authority | Auditor verdict never acts automatically. Matt still issues `lock §11`, `start build`, commit, or push. |
| Drift control | Blocking verdicts require explicit resolution before implementation proceeds. |
| Audit noise | Tiny implementation choices and signed-spec details are out of scope, preventing bureaucracy. |
| Persistence | Reports are local under gitignored `audit_outputs/decision_audits/`; no Blackboard / production / operator state writes. |
| Prompt drift | Prompt is locked and test-pinned. |

---

## §9 Downstream Integration

### Build-order recommendations

When a major lane is selected, the primary assistant creates a packet explaining:

- recommended lane,
- why now,
- why not alternatives,
- current runtime/test/audit state,
- constraints from Matt,
- expected next action.

The auditor report is then summarized in chat. If the verdict is blocking, the assistant must not proceed to §11 lock or implementation until Matt explicitly resolves it.

### §11 spec locks

For new subsystems, the packet should be created before Matt signs §11 if:

- the subsystem opens a new state surface,
- the spec changes Guardrails 8-12,
- the spec creates a new external data/API dependency,
- the spec displaces another roadmap item.

### Activity log

If the decision affects current project direction, `PROJECT_ACTIVITY_LOG.md` records:

- packet file path,
- report path,
- verdict,
- whether Matt accepted, revised, deferred, or overrode the recommendation.

### Handshake

`PROJECT_HANDSHAKE.md` records only the current outcome, not every packet. Example:

```text
Independent Decision Auditor reviewed the DKIM/SPF/DMARC vs Document Metadata choice;
verdict proceed_with_notes; Matt accepted DKIM/SPF/DMARC next.
```

---

## §10 V2 Deferrals & Explicit Non-Goals

| Deferral | Rationale |
|---|---|
| Multi-model panel | One independent model is enough for v1. Panels add cost and complexity. |
| Automatic packet generation from chat history | Too easy to include stale or private context. v1 packets are explicit and reviewable. |
| GitHub PR checks | Useful later, but v1 is local operator tooling. |
| Browser/UI workflow | CLI + Markdown files are sufficient now. |
| Persistent decision database | Local Markdown reports and trackers are enough; no new state surface. |
| Auditing every small decision | Would slow the project and create alert fatigue in governance. |
| Replacing Matt's judgment | Explicitly out of scope. The auditor informs; Matt decides. |

---

## §11 Lockdown Signature

This spec is locked when the block below is filled in. The implementation receipt for the workflow must cite this file by section number.

```text
LOCKED BY:  Matt Nichol (operator)
LOCK DATE:  2026-05-24
COMMENTS:   All §2 architectural decisions (D1-D16) locked end-to-end during
            the 2026-05-24 spec-first session. Highlights:
              - Decision Auditor lives in audit_tools/decision_audit_runner.py
                (governance tooling, NOT product runtime); no core/ module
                imports it.
              - Decision packets live under decision_audit_inputs/ at the
                workspace root and use the locked six-section Markdown
                contract: Decision Under Review, Primary Recommendation,
                Rationale Given, Rejected Alternatives, Current Project
                State, Constraints / Guardrails.
              - Reports land under audit_outputs/decision_audits/, gitignored
                by the existing audit_outputs/ rule.
              - .env handling matches the code-audit runner: XAI_API_KEY and
                optional XAI_MODEL only; never printed, logged, persisted,
                or echoed.
              - Default model = grok-4; auditor prompt is a locked constant.
              - Closed verdict enum: proceed, proceed_with_notes,
                revise_before_proceeding, defer, operator_decision_required.
              - Fail-closed gate: revise_before_proceeding, defer, and
                operator_decision_required block implementation until Matt
                explicitly resolves the audit. proceed / proceed_with_notes
                still require Matt's normal explicit command
                (lock §11, start build, commit, push, etc.); the auditor
                never acts for the operator.
              - Required audit triggers: next build-lane selection, new §11
                spec locks that open a new subsystem or persistent surface,
                Guardrail 8-12 changes, data-egress / external-API
                decisions, new tenant / operator / production state
                surfaces, gold-plating vs necessary-quality disputes,
                roadmap reversals, runtime-affecting pricing/package
                decisions, and any explicit anti-drift request from Matt.
              - Non-triggered work: small bug fixes, test fixes, tracker
                receipts, and implementation choices already inside a
                signed spec.
              - Data-minimization boundary: no .env, secrets, raw client
                emails, raw financial strings, GitHub tokens, or private
                audit outputs may appear in decision packets. Packet
                validation must fail-fast on known secret markers before
                any network call.
              - Operator authority preserved end-to-end. Matt can override
                any verdict; the override must be written into the
                packet/result receipt with the reason.
              - Tracker integration: decision-audit reports for build-order
                decisions are cited in PROJECT_ACTIVITY_LOG.md and
                PROJECT_HANDSHAKE.md when they affect current direction.
              - §7 20-test gate is the closure contract. Partial
                implementations do NOT close §4. Implementation receipt
                cannot claim closure until one self-audit packet has been
                run against the "Decision Auditor next" build-order choice.
              - Implementation work does NOT begin until Matt issues the
                explicit "start build" signal in chat.
```

Once signed:

- Every implementation receipt must cite this file by section number.
- Any deviation from a §2 locked decision requires a new spec revision.
- The §7 gate test list is the closure contract.
- Implementation still requires Matt's explicit `start build` signal after signature.
