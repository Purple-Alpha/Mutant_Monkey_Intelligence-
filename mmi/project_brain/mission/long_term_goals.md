# Long-Term Goals

**Horizon:** 12 months → 5 years  
**Last updated:** 2026-06-25  
**Authority:** Strategic direction sheet. Product thesis lives in `VISION.md` (edit rarely). Tactical queue lives in the scoreboard + project brain status files.

---

## North Star (product thesis)

Build a **self-evolving, trigger-based cybersecurity defense swarm** that:

1. **Detects** threats across surfaces (email today; identity, endpoint, auth later)
2. **Defends** autonomously when confidence is high — with kill switch, audit, and reversibility
3. **Learns** from every attack without cross-tenant data leakage
4. **Stays accountable** — signed policy, promotion gates, human loop for high-liability actions
5. **Reaches SMBs through MSPs** — trust layer MSPs bundle into every stack

Full thesis and seven non-negotiables: `VISION.md`

---

## Commercial Arc (Stage A → B → C)

| Stage | What we ship | Horizon | Revenue meaning |
|-------|----------------|---------|-----------------|
| **A — Analyze + Recommend** | Score, evidence reports, MSP audit trail. No autonomous action. | Now → ~12 mo | Sellable decision-support (Inbox Shield wedge) |
| **B — Auto-Defend Obvious** | Auto-quarantine high-confidence; escalate ambiguous. M365/GWS connectors. | ~12–24 mo | Recurring MSP revenue; first real autonomy |
| **C — Self-Evolving Swarm** | Cross-surface response, threat-intel loop, kill-switch-bounded autonomy | ~3–5 yr | Category leader or acquisition target |

Each stage is **independently sellable** and funds the next. Long-term success does not require shipping Stage C this year.

---

## Engineering Arc (M1 → M5)

Project-brain milestones sequence the *how* behind the product arc:

| Milestone | Goal | Unlocks |
|-----------|------|---------|
| **M1** Control plane restored | One command → one honest next action | Operator can steer without governance walls |
| **M2** Contract queue clean | Drafts, signed contracts, GATED, promotion targets never mixed | Safe scaling of parallel agent lanes |
| **M3** Build pipeline stable | Build only from signed authority; tests + evidence tied to contract | Repeatable agent factory |
| **M4** Governed runtime spine | GATED → GOVERNED_AGENT promotion only after review | Production dispatch with boundaries |
| **M5** Demo / revenue asset | Usable proof inside security + authority limits | MSP-facing demo, sales motion |

**Active now:** M1 (nearly complete). Short-term depth work (#19) advances M2 + M3.

---

## Swarm Build Target

**#1 TARGET (scoreboard):** Full **70-agent governed Blue Team swarm** — non-reducible inventory from architecture map.

### Breadth runway (primary path today)

- Wrap existing pure detectors with §11-signed Agent Design Contracts
- Evidence Stage 1 synthetic → tests → completion gate → `GATED` → `GOVERNED_AGENT`
- **Progress:** 40 / 70 at `GOVERNED_AGENT` (2026-06-25)
- **Not in default registry / no production dispatch** until promotion review

### Depth stack (gated)

- Agents **#84–#94** — DEPTH gate **CLOSED** (BS-D3)
- Blocked until Production Evidence Store + real-data controls + separate operator authorization
- Agents **#54–#60** carry `NEEDS_REAL_DATA`

### Autonomy lane (gated)

- **STAGE_B gate CLOSED** — e.g. #38 Containment
- No autonomous containment until signed Stage B authorization

---

## Layered Defense Model (design tree)

Six layers, built as governed agents with contracts:

| Layer | Role | Examples in flight |
|-------|------|-------------------|
| 1 Command | Orchestration, context, triage | #1–#3 GOVERNED_AGENT |
| 2 Detection | Facts-only indicators from detectors | #23–#31, #39, … |
| 3 Verification | Confirm before high-stakes inference | #11, #19 (in build), VPV workflow |
| 4 Evidence | Packages, strength, audit artifacts | #46, #49, #50 |
| 5 Response | Containment, blocking (Stage B+) | #38 held |
| 6 Learning | Policy mutation, cross-tenant intel | Stage C; adversarial review required |

Long-term: every high-liability path goes through **detect → verify → evidence → human or signed auto-action**.

---

## Research Branches (design now, build later)

Captured under `mmi/project_brain/architecture/` — **not build authorization:**

| Topic | DEC refs | Status |
|-------|----------|--------|
| Purple Translation Layer | MMI-DEC-223 | Defensive-first; unified fact schema draft |
| Agentic Swarm Command Center | MMI-DEC-226 | Orchestrator / sub-agent research |
| Adversarial Resilience Harness | MMI-DEC-227 | Lab-only breaker concept |
| Geo-Context (#43) | MMI-DEC-222 hold | Needs more research |

High-liability concepts (active deception, exploit, scanning) stay parked behind separate legal/safety authority.

---

## Success Markers

### 12-month (Stage A solid)

- [ ] Operator control plane trusted daily (`pm_voice` + verify PASS)
- [ ] BREADTH runway ≥ 50 / 70 `GOVERNED_AGENT` OR depth lane #19–#70 contract stack materially advanced
- [ ] MSP-facing evidence demo path (M5 probe) with 0 blocking governance drift
- [ ] Command spine (#1–#3) + verification lane (#11, #19, VPV) integrated in synthetic end-to-end test story
- [ ] No production dispatch without explicit promotion record

### 24-month (Stage B credible)

- [ ] STAGE_B gate opened with signed authorization
- [ ] Live M365/GWS connector path for high-confidence auto-quarantine
- [ ] Real-data agents (#54–#60) on Production Evidence Store
- [ ] DEPTH gate opened (BS-D3 cleared)
- [ ] Recurring MSP revenue from bundled trust layer

### 3–5 year (Stage C direction)

- [ ] Cross-surface swarm response with kill-switch supremacy
- [ ] Continuous learning loop with adversarial-suspicious update escalation
- [ ] Tenant-isolated cross-tenant signature sharing
- [ ] Category-defining audit moat — autonomous action that customers trust

---

## Principles That Do Not Expire

From `VISION.md` non-negotiables + MMI doctrine:

1. Kill switch always wins
2. Every autonomous action audited and reversible
3. Tenant isolation sacred
4. Promotion to production is signed
5. Adversarial-suspicious updates → human review
6. Client-facing / high-dollar actions → human in the loop (e.g. vendor payment approval)
7. Scoreboard generates candidates; rubric ranks; **Matt selects**; decisions are recorded

---

## How This Sheet Relates to Daily Work

| Question | Read this |
|----------|-----------|
| What do I do this week? | `mission/short_term_goals.md` + `status/active_task.md` |
| What milestone am I advancing? | `mission/milestone_map.md` |
| What is the product end-state? | `VISION.md` + this file |
| What is the next build row? | Scoreboard header + `python3 scripts/mmi_pm_voice.py` |

Re-read this file at the start of each major build cycle. Update only when the strategic arc changes — not when a single agent ships.
