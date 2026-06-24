# MMI INTAKE — MSP Pilot Motion (Todd / CMIT Kelowna · Commercial Lane)

**Intake ID:** `INTAKE-2026-06-24-003`

**Mission map waypoint:** Stage A · `a04`

**Date filed:** 2026-06-24

**Source:** Claude advisory deliverable → Cursor execution lane (Matt relay)

**Decision closeout:** `MMI-DEC-129` (intake filed — pilot evidence not yet produced)

**Routing outcome:** **VERIFY** — pending P0 scoping + pilot evidence; not ACCEPT pre-evidence

**Matt approval required:** YES before live third-party mail access; YES for any §11 or build authorization emerging from this motion

---

## Authority

| Role | Who | Boundary |
|---|---|---|
| Signing authority | Matt Nichol | Routing, §11, Safe-Stop exit, ACCEPT/REJECT |
| Validator | Todd Chapman (CMIT Solutions Kelowna) | Feedback + on-record sign-off; **not** governance authority |
| Advisory | Claude | Prose/plans only |
| Execution | Cursor | Repo write, intake record, MMI closeout |

**Companion docs (non-authority):**

- `1. Business_Operations/First_Pilot_Strategy.md` — retrospective / detect-only framing aligns
- `1. Business_Operations/Client_Documents/Todd_Tuesday_MSP_Call_Anchor_Card.md` — operator anchor (Matt's notes)
- `Frontier_Intake_Log.md` — Todd door logged 2026-06-03 (partial signal; not D10)
- `mmi/MMI_MISSION_MAP.md` — commercial lane (beside Defender, BEC/vendor, billable-time)

---

## 1. Motion

Stand up a controlled, **detect-only** pilot of Mutant Monkey Inbox Shield with one real MSP (Todd / CMIT Kelowna) to gather **hard evidence** of buyer value: real fraud catches with full evidence packets, triage time saved, and validator sign-off on record. Evidence-first — this intake cannot reach **ACCEPT** until the pilot produces measurable artifacts.

---

## 2. Scope

| In | Out |
|---|---|
| Detect-only analysis of email flow for **1–3 agreed SMB clients** of Todd's (set at P0) | Any autonomous action on mail (quarantine, reply, delete) |
| Evidence-packet generation (headers, auth, look-alike/thread-forgery reasoning) | Production deployment or `GOVERNED_AGENT` activation |
| Triage time-saved measurement vs Todd's documented baseline | Multi-tenant rollout beyond agreed clients |
| Validator feedback capture (would deploy / would recommend) | Any §11 signature or build authorization off this intake alone |

**Default integration posture (until P0 overrides):** retrospective / bounded batch on operator-controlled machine per `First_Pilot_Strategy.md` §3 — **no live mailbox wiring** until legal/consent gate cleared.

---

## 3. Detection posture (non-negotiable)

- **Detect-not-enact.** MMI surfaces evidence; it takes no action on Todd's clients' mail.
- **AUTH-5 (autonomous task selection): blocked** system-wide.
- **Safe-Stop:** Matt-only exit authority. Kill switch live for the full pilot window.
- Read-only / advisory mode only — no write path into client mailboxes.
- **Privacy Filter `#93`** (adversarially hardened) in-path before any client content processing.

---

## 4. Success criteria (evidence-tied)

**ACCEPT** requires hard evidence, not impressions. Numbers **confirmed with Todd at P0**:

| Criterion | Target (provisional — P0 confirms) |
|---|---|
| Real fraud signal | ≥1 real fraud attempt detected with complete evidence packet during window **OR** documented zero-TP baseline (not a silent gap) |
| False positives | Within **Todd-agreed tolerance** — **TBD at P0** |
| Billable time | Measured triage time saved vs **Todd baseline before-number** — **TBD at P0** |
| Validator | Todd on-record: would deploy / would recommend |

---

## 5. Data and privacy handling (hard gate)

Third-party email (Todd's clients) — not Matt's own data.

- **Written consent + data-processing scope required before any live-mail access.** No live mail until closed.
- **Prefer replayed/sanitized corpus first** if legal scoping isn't closed — proves detection without exposure.
- Tenant baseline ingestion requires **operator (Matt) approval above defined risk threshold** (OQ-5 high-impact triggers).
- Legal scoping for client email + reputation/attribution = **prerequisite**, not parallel optional work.

**Status:** legal/consent artifact — **NOT ON DISK** at intake filing; Matt must authorize language before live-mail steps.

---

## 6. Phases

| Phase | Gate | Status |
|---|---|---|
| **P0** Scoping call w/ Todd | Clients, access mode (live vs replay), duration, FP tolerance, commercial terms | **OPEN** |
| **P1** Consent + data setup | Legal/consent cleared · privacy filter · baseline approval | BLOCKED on P0 + legal |
| **P2** Pilot run | Detect-only window (length set at P0) | BLOCKED |
| **P3** Evidence review | Evidence packets + time-saved metrics assembled | BLOCKED |
| **P4** Decision gate | Matt routes ACCEPT / PARK / REJECT → updates this intake + DEC trail | BLOCKED |

---

## 7. P0 parameters (Todd-dependent — fill at scoping)

| Parameter | Value |
|---|---|
| SMB client count | **TBD** (target 1–3) |
| Client names / IDs | **TBD** |
| Access mode | **TBD** — default proposal: retrospective batch / sanitized replay first |
| Pilot window length | **TBD** |
| FP tolerance | **TBD** |
| Commercial terms | **TBD** — free pilot vs paid; no pricing locked in strategy docs |
| Todd baseline triage minutes | **TBD** — required for billable-time thesis |

---

## 8. Evidence required before ACCEPT

- Detection logs / evidence packet IDs (paths or MMI record refs)
- Time-saved measurement vs documented baseline
- Todd sign-off artifact (file path or intake appendix)
- Attestation: no write-path or autonomous action occurred; Safe-Stop intact

---

## 9. Proposed routing (Matt sets)

**VERIFY** at filing (MMI-DEC-129). Drop to **PARK** if P0 does not occur. **ACCEPT** only after §8 evidence. Final outcome is Matt's call.

---

## 10. Explicit non-authorization

This intake does **not** authorize:

- Live third-party mail access (until P1 legal/consent gate)
- §11 signatures or build authorization
- `GOVERNED_AGENT` promotion or production dispatch
- AUTH-5 or registry-fed routing
- Cyber insurance D10 worksheet completion (separate track)

Matt Nichol — intake filed by Cursor execution lane (MMI-DEC-129).
