# Operating Doctrine — 14-Day Trial

**Status:** DRAFT pending operator activation signature (§11 below). Time-bounded process artifact, not a permanent contract.
**Authority:** Matt is operator and trial decider. This artifact records the rules of the trial and the evidence basis for the end-of-trial decision. It does not change permanent project governance until Matt elects to keep it past day 14.
**Scope:** Defines a measured 14-day trial of the current operating system so that the keep/tighten/loosen/rollback decision can be made from evidence instead of feel.

---

## §1 Purpose

The project has accumulated a set of operating rules over the last several work sessions (queue-driven defaults, gate-enforced completion, rubric demotion, no AI-authored authority, technical-verification-layer role for the assistant). Some are likely keepers. Some may be drag. Right now there is no evidence basis to tell them apart, only one full work session of vibe.

This artifact runs them as a single coherent doctrine for 14 calendar days and then forces a retrospective against named evidence. The output of the retrospective is one of four decisions (§7). The trial is the cheaper-proof step for governance changes that would otherwise be locked in by repetition rather than measurement.

This is *not* a permanent doctrine. It is a trial of a candidate doctrine. The candidate doctrine becomes permanent only if §7 decision 1 ("Keep it") is selected at the retrospective.

---

## §2 Trial Dates

**Proposed start:** 2026-05-26 (today, on operator activation signature in §11).
**Proposed end:** 2026-06-09 end of day (14 calendar days inclusive of start day).
**Retrospective day:** 2026-06-10. Decision rendered in §7 by end of that day or operator-elected extension recorded in `PROJECT_ACTIVITY_LOG.md`.

Dates lock at signature. If Matt signs later than 2026-05-26, both dates shift forward by the same offset; retrospective day shifts to (end + 1).

The trial may be terminated early by Matt at any time (§9) — early termination still produces a retrospective entry but renders the decision against partial data.

---

## §3 Operating Rules Being Tested

The eight rules below run as a single coherent doctrine for the trial window. They cannot be modified during the trial (§8). Each rule is named so the retrospective can attribute outcomes to specific rules instead of to the doctrine as a whole.

| ID | Rule | Source artifact |
|---|---|---|
| R1 | Matt decides. Operator is final authority on all project moves; rubrics, gates, and AI recommendations are inputs, never deciders. | NorthStar Operating Constitution (discussion 2026-05-26) |
| R2 | Queue gives default next item. `PROJECT_BUILD_AND_AUDIT_QUEUE.md` §4 names the next action; operator may override at any time. | `PROJECT_BUILD_AND_AUDIT_QUEUE.md` §2 / §4 |
| R3 | Cursor builds and drafts. Cursor does not score, does not approve, does not paraphrase completion claims. Technical Verification Layer role. | NorthStar Operating Constitution |
| R4 | Operator project-manages and verifies. Sequencing, ordering, and "this is done" calls live with Matt. | `PROJECT_BUILD_AND_AUDIT_QUEUE.md` §5 canonical-roles rule |
| R5 | Grok audits completion. Negative-feedback only — identify deviations, do not score or approve. | `audit_tools/complete_gate.py` v1.1 Grok prompt |
| R6 | Gates fire only at ready / done / ship / sign-off. Not during normal exploration or operator-directed work. | `audit_tools/complete_gate.py` v1.0 docstring |
| R7 | Rubrics are advisory only. They surface tradeoffs; they do not gate work and do not decide promotion. | `Compliance_and_Trend_Watch_Process.md` §1.1 supersession |
| R8 | No "complete" without fresh audit evidence. A claim of done requires a fresh Grok audit output whose packet hash matches the current touched files, with no open blocking findings. | `audit_tools/complete_gate.py` v1.1 freshness rule + `PROJECT_BUILD_AND_AUDIT_QUEUE.md` §3 Audit List item 4 |

Items not in this list (e.g. spec-first discipline, seven non-negotiables in `VISION.md`, the tenant-isolation principle) are *not* on trial. They are project invariants and continue to apply. The trial tests only the eight operating-doctrine rules above.

---

## §4 Success Criteria

The eight questions below are answered at the retrospective. Each question pairs with a named evidence source so answers come from artifacts, not memory. "Yes / no / partial" with a one-sentence evidence citation is the expected answer shape; long narrative answers are a smell.

| # | Question | Evidence source |
|---|---|---|
| S1 | Did the doctrine reduce how much Matt had to micromanage? | Operator self-report **plus** count of "menu mode" / "what should I pick" moments in this trial's chat transcripts vs. prior comparable period. |
| S2 | Did the queue answer "what's next" without forcing Matt to choose from menus? | Number of turns in the trial where the next action was unambiguous from `PROJECT_BUILD_AND_AUDIT_QUEUE.md` §4 vs. number of turns where the operator had to disambiguate. |
| S3 | Did gates protect completion without blocking collaboration? | `audit_outputs/` — count gate firings; count blocking findings; count operator overrides; count *unjustified* blocks (blocks that the operator judged wrong in hindsight). |
| S4 | Did Grok catch anything useful? | `audit_outputs/` and `audit_outputs/drift_incidents/` — list specific findings that altered work; list findings that were ignored as noise; ratio is the answer. |
| S5 | Did Cursor work packets become clearer? | Worker manifests in `audit_outputs/pending/*.manifest.json` reviewed for completeness; touched-file coverage failures counted; manifest-verification errors counted. |
| S6 | Did the doctrine avoid AI-authored authority claims? | Trial-window scan of `4. Product_Roadmap/*.md`, `audit_tools/` constants, and any newly-landed governance text for AI-authored "policy says" / "you must" / "the framework requires" phrasing that is not operator-stated. |
| S7 | Did the project move closer to revenue or signed specs? | Count of `§11 SIGNED` markers added during the trial; count of MSP discovery conversations logged in `THREAT_INTEL_LOG.md`; any revenue lane progress in `REVENUE_MAP.md`. |
| S8 | Did anything feel slower for no safety benefit? | Operator self-report **plus** any gate firing that produced no useful finding and added more than ~10 minutes to a work session; counted from `audit_outputs/` timestamps. |

Each criterion gets a one-line answer in the §7 retrospective record. Answers that cite "feel" without an evidence source are flagged as a doctrine weakness regardless of which way they cut, because evidence-free conclusions are what the trial exists to avoid.

---

## §5 Failure Signals

The trial can produce a clear-fail signal before day 14. Any of the signals below trigger an operator decision to continue / pause / abort early — they are not auto-aborts, but they are documented triggers so a "this is going badly" signal does not get silently absorbed.

| ID | Signal | Detection |
|---|---|---|
| F1 | Operator overrides a gate more than 3 times during the trial for non-emergency reasons. | Count drift-incident records in `audit_outputs/drift_incidents/` with `severity: warning` and `finding_type: operator_override`. Threshold of 3 is informational, not auto-abort. |
| F2 | A gate produces a blocking finding that the operator judges wrong, more than once. | Operator-marked "wrong block" entries in `PROJECT_ACTIVITY_LOG.md` during trial window. |
| F3 | Queue goes stale — no edit to `PROJECT_BUILD_AND_AUDIT_QUEUE.md` for 7+ consecutive days while project work continues. | `git log` on the queue file vs. project activity in the same window. (Note: queue's own drift signal is 14 days outside a trial; during trial the threshold tightens to 7 because the trial is itself only 14 days long.) |
| F4 | AI-authored authority claim lands in any tracked file without operator authorship attribution. | Spot-check of trial-window diffs in `4. Product_Roadmap/`, `audit_tools/`, root governance files. Same scan as success-criterion S6 but counts as a failure signal if non-zero. |
| F5 | Grok audits return clean every time with no useful findings for 5+ consecutive runs. | `audit_outputs/` review. May indicate rubber-stamp behavior, prompt drift, or genuinely-clean work; operator judges which. Counted as a signal only if combined with at least one missed deviation the operator catches manually. |
| F6 | "Complete" wording ships in any artifact without fresh audit evidence. | Search trial-window diffs for "complete" / "done" / "signed" wording on items lacking an `audit_outputs/<task>_<timestamp>.md` whose packet hash matches. Gate is supposed to prevent this; F6 firing means the gate was bypassed and not caught. |

Failure signals do not in themselves end the trial. They inform the §7 retrospective and may prompt an operator-elected early abort (§9). An early-abort retrospective still produces a §7 decision but explicitly flags the partial-data condition.

---

## §6 Evidence To Review

The artifacts listed below are the *only* sources consulted in the §7 retrospective. The list is frozen for the trial (§8) so the retrospective is not made interpretable-after-the-fact by selectively expanding the review surface.

- `PROJECT_BUILD_AND_AUDIT_QUEUE.md` — queue evolution; were items reordered, removed, or added during the trial; does the queue match what actually happened.
- `PROJECT_HANDSHAKE.md` — current-active-focus evolution; did the handshake stay in sync with the queue per the canonical-roles rule.
- `PROJECT_ACTIVITY_LOG.md` — every major event logged during the trial.
- `PROGRESS.md` — task closures during the trial window.
- `audit_outputs/` — all Grok audit outputs in the trial window; count, freshness, hash-match rate.
- `audit_outputs/drift_incidents/` — every drift incident (operator override, missing-file, blocking-finding, etc.) recorded in the trial window.
- `audit_outputs/pending/*.manifest.json` — worker manifests produced during the trial; coverage rate; verification failures.
- Any spec in `4. Product_Roadmap/` that was edited during the trial — pre-/post-diff for governance text, sign-off state, scope.
- Any Cursor/Grok handoff summary recorded during the trial — chat-side summaries that captured handoff state.
- `git log --since=2026-05-26 --until=2026-06-09` (or whatever the locked trial window is) for the project as a whole — commits, scope, frequency.

Items *not* in this list (e.g. older `audit_outputs/` runs from before the trial, prior-period `PROJECT_ACTIVITY_LOG` entries) may be referenced for comparison if the retrospective explicitly cites them as comparison data, but they cannot be used to argue the trial's success/failure on their own.

---

## §7 End-of-Trial Decisions

At the retrospective, exactly one of the four decisions below is selected and recorded in `PROJECT_ACTIVITY_LOG.md` with the §4 success-criterion answers and §5 failure-signal counts attached.

| # | Decision | Meaning |
|---|---|---|
| D1 | **Keep it.** | The doctrine is working. Rules R1–R8 become permanent project governance. This artifact's §3 promotes to a signed governance reference; `PROJECT_BUILD_AND_AUDIT_QUEUE.md` continues to operate as currently shaped. |
| D2 | **Tighten it.** | The doctrine is helping but gates / queue rules need sharpening. Specific tightenings are listed in the retrospective entry. New tightened doctrine starts a fresh evaluation window (not necessarily another full trial). |
| D3 | **Loosen it.** | Doctrine is too much ceremony for the value delivered. Keep Grok audit at completion; reduce process around it. Specific looseninngs listed in the retrospective entry. |
| D4 | **Rollback part of it.** | Some rules are keepers, others are drag. Retrospective entry lists which of R1–R8 stay, which retire, and what (if anything) replaces the retired ones. |

The retrospective entry includes:
- §4 success-criterion answers (S1–S8) with evidence citations.
- §5 failure-signal counts (F1–F6).
- Selected decision (D1–D4) with rationale.
- Specific rule-level keep/tighten/loosen/rollback notes if D2/D3/D4.
- Next-period operating mode (effectively immediately on decision-record landing).

---

## §8 What Cannot Be Changed During Trial

These are frozen for the trial window so the retrospective is interpretable. Any urge to change any of them during the trial is captured in a "deferred to retrospective" list (separate scratch artifact or chat-side notes), not merged into this file until §7.

- The eight operating rules in §3 (R1–R8).
- The eight success criteria in §4 (S1–S8).
- The six failure signals in §5 (F1–F6).
- The evidence list in §6.
- The four decision options in §7 (D1–D4).
- The trial dates in §2 once signed.
- The "do not change during trial" list itself (this §8). No meta-edits either.

If a rule in §3 is genuinely broken in a dangerous way mid-trial, the operator's tool is §9 (override or abort), not silent edits to this file. The whole point of the freeze is to keep the trial measurable.

---

## §9 What Matt Can Override Anytime

Operator authority is never on trial. The doctrine exists to serve the operator, not constrain them. Specifically, during the trial Matt can do any of the following without invalidating the trial:

- **Override any single gate firing** with a recorded reason. The override is logged in `audit_outputs/drift_incidents/` as a warning-severity record per the existing `complete_gate.py` contract. Overrides are data, not failures.
- **Reorder, add, or remove items in `PROJECT_BUILD_AND_AUDIT_QUEUE.md`** at any time. Queue is canonical for ordering; operator is canonical for the queue.
- **Reject any Cursor or AI recommendation** at any time. No appeal mechanism. Rejection is logged minimally in the chat or activity log so the retrospective can count it.
- **Declare a specific item exempt from the trial rules** with a recorded reason. The exemption is captured in `PROJECT_ACTIVITY_LOG.md`; the retrospective accounts for exempted items separately.
- **Terminate the trial early.** Operator-elected early termination produces a §7 retrospective entry with a "partial data — terminated day N" flag. Early termination is not a failure of the trial; it is a valid output.
- **Direct work outside the queue.** R2 says the queue is the default next item, not the only allowed item. Operator-directed work outside the queue is a normal pattern, not an exception; it just gets logged so the retrospective can count "queue-directed vs. operator-directed" work without bias.

The override list is exhaustive for trial-relevant overrides. It does not list operator authority over `VISION.md` non-negotiables, tenant isolation, or spec-first discipline because those are project invariants outside trial scope (§3 closing paragraph).

---

## §10 Grok Audit Requirements

The trial does not change Grok's role. Grok continues to operate as the negative-feedback completion auditor per R5 and per `audit_tools/complete_gate.py` v1.1.

Three trial-specific Grok audit hooks:

1. **No mid-trial doctrine audit.** Grok is not asked "is the doctrine working" at any point during the trial. That would replace operator judgment with an external judgment, which defeats the trial's purpose (R1 says Matt decides). Grok's mid-trial scope stays exactly as it is in the gate today.
2. **Optional end-of-trial retrospective audit.** After the operator drafts the §7 retrospective entry, the operator may elect to run a Grok audit with this exact prompt:

   > Identify any evidence in the supplied artifacts that contradicts the operator's retrospective conclusions, or any major piece of evidence the retrospective failed to consider. Do not score the doctrine. Do not approve or reject the operator's decision. Report only contradictions and omissions.

   The audit packet for the retrospective audit contains: this artifact, the §7 retrospective entry, and every item in §6 Evidence To Review. The audit output is appended to the retrospective record but does not override the operator's §7 decision. The operator may, on reviewing the audit, amend the retrospective entry; the original draft is preserved in `PROJECT_ACTIVITY_LOG.md` so the amendment is itself auditable.

   The retrospective audit is *optional*. Operator may skip it. Skipping is recorded.

3. **Audit-the-auditor cadence.** Grok itself is on trial through F5 ("rubber-stamp behavior"). The cadence below produces evidence for that signal instead of leaving it to feel:

   - **Weekly adversarial seeding.** Once per 7 calendar days during the trial, take a recent gate-audited packet, plant one known boundary violation (e.g. add the phrase `SOC 2 attested` outside the `Compliance_and_Trend_Watch_Process.md` §5.3 carve-outs, or break an internal cross-reference between sections), re-run the gate against the seeded packet, and confirm Grok flags the seeded item as Blocking. If Grok misses the seeded violation, that is a rubber-stamp signal: log a drift incident with `finding_type: rubber_stamp_signal`, surface the failure in the next §7 retrospective input, and either harden the gate prompt or feed the case forward to the retrospective for a doctrine-level decision. Seeded packets are throwaway — the seeded file is reverted after the test run, and the test itself is not a real completion claim.
   - **Cross-audit (operator-elected).** When operator judgment calls for it — typically on §11 sign-off audits — run the same packet through a second model and compare. Disagreements with Grok are signal, not noise, and are recorded in the trial-window evidence trail per §6. Cross-audit is operator-driven; it does not auto-fire and does not gate completion.
   - **Cadence is operator-driven, not gate-enforced.** A skipped weekly seeding is recorded in `PROJECT_ACTIVITY_LOG.md` as `audit-the-auditor skipped, week N — reason: <text>` so the §7 retrospective can count skipped weeks as evidence. The cadence itself is on trial — if it generates more drag than signal during the 14 days, the retrospective decision in §7 may drop or alter it.

   This hook is the named mechanism that produces the "missed deviation the operator catches manually" event referenced in §5 F5 detection. F5 stays scored as written; this hook just gives it a deliberate detection path instead of relying solely on accidental discovery.

---

## §11 Trial Activation Signature

**Trial is DRAFT until signed below. Dates in §2 lock at signature.**

> Signature line (operator-applied):
>
> *Operator-Authored Trial Activation — Matt Nichol, YYYY-MM-DD:*
>
> [Replace this placeholder with operator-authored sentence acknowledging the eight rules in §3, the freeze in §8, and the override scope in §9. On landing, the signature line becomes the trial-start marker and the dates in §2 lock. No Cursor / AI authorship inside this signature block.]

Activation actions on operator signature (operator-performed or operator-directed; not auto-applied by this file):

1. Log a `PROJECT_ACTIVITY_LOG.md` entry that names the trial window and points at this artifact.
2. Optional: add a single-line reference to this artifact in `PROJECT_HANDSHAKE.md` under the queue pointer, so anyone reading the handshake first sees the active trial. (Operator decision — not auto-applied.)
3. Optional: add this artifact to `MASTER_INDEX.md` under Product Roadmap. (Operator decision — not auto-applied.)

The trial does *not* change any signed §11 contract in any other Product Roadmap deep-dive. It governs the *operating mode* during which signed specs continue to be built, audited, and shipped per their own contracts.

---

## §12 Cross-references

- `PROJECT_BUILD_AND_AUDIT_QUEUE.md` — the queue this trial leans on for R2 and R4.
- `PROJECT_HANDSHAKE.md` — current active focus; trial does not change focus-selection mechanics.
- `PROJECT_ACTIVITY_LOG.md` — landing surface for trial activation, drift incidents, exemptions, and the §7 retrospective entry.
- `audit_tools/complete_gate.py` — gate implementing R5, R6, R8. v1.1 freshness contract is the trial's mechanical floor.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` — §1.1 supersession is the basis for R7.
- `VISION.md` — seven non-negotiables. Out of trial scope; remain invariant.

---

**End of trial draft. Pre-§11. No tracker updates, no doctrine activation, and no governance promotion are authorized by this document until operator signs §11.**
