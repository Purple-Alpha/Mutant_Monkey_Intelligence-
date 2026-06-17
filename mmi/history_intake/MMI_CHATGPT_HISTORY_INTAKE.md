# MMI_CHATGPT_HISTORY_INTAKE.md — Chat-History Intake & Classification

> **NON-AUTHORITATIVE INTAKE — EVIDENCE, NOT AUTHORITY.**
> This file is an MMI classification pass over chat-history material (ChatGPT / Claude /
> Gemini / Grok / Cursor sessions) and the repo artifacts those sessions produced. It
> **does not authorize build, research, design, or promotion**, and it **does not change**
> the dispatcher, scoreboard, gate registry, decision log, protocol, or routing rules.
> Current routing authority remains: `mmi/MMI_GATE_REGISTRY.md`, `mmi/MMI_DECISION_LOG.md`,
> and `scripts/mmi_dispatch.py --verify`. Matt must explicitly authorize any next phase
> after reviewing this map.
>
> **Phase:** MMI_CHATGPT_HISTORY_INTAKE_AND_CLASSIFICATION (documentation/classification only)
> **Pass type:** Documentation/classification only — does not modify dispatcher, routing,
> scoreboard, handshake, or automation.
> **Compiled:** 2026-06-15 (repo pass); reconciled 2026-06-16 (`mmi/history_intake/` cleanup)
> **Authority:** Matt Nichol — sole signing authority. MMI classifies; Matt decides.

---

## Related intake files (same folder)

| File | Role |
|---|---|
| `README.md` | Folder index + authority-bleed prevention rule |
| `MMI_CHATGPT_HISTORY_MASTER_INDEX.md` | Pointer to Windows deduplicated master (secondary) |
| `MMI_CLAUDE_CURSOR_HISTORY_INTAKE.md` | Claude/Cursor compendium quarantine (golden/parked/overclaim) |
| `MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md` | Lane-selection session history — `NEEDS_MMI_REVIEW` only |

---

## Classification key (labels used below)

| Label | Meaning |
|---|---|
| `AUTHORITATIVE_CURRENT` | Currently governs the project; live source of truth |
| `SUPPORTED_BY_REPO` | Idea is backed by committed code/specs in the repo |
| `SIGNED_BUT_UNBUILT` | §11/§13-signed contract exists; code not (fully) built |
| `BUILT_NEEDS_VERIFICATION` | Code/claim exists but needs a fresh repo/evidence check |
| `RESEARCH_INPUT` | Research/evidence material feeding decisions, not a spec |
| `CONCEPT_IDEA` | Idea captured; no contract, no authorization |
| `PARKED_DRAFT` | Deliberately set aside; untracked or flagged non-authoritative |
| `SUPERSEDED` | Replaced by newer authority; keep for history only |
| `DUPLICATE` | Overlaps another artifact; risk of two sources of truth |
| `CONTRADICTION` | Conflicts with another item; needs reconciliation |
| `NEEDS_MMI_REVIEW` | Possibly valuable but unclassified until MMI/Matt reviews |
| `DO_NOT_USE` | Must not become authority (sample/illustrative/disclaimed) |

> **Preservation rule applied:** good and bad ideas, contradictions, and superseded items
> are all preserved. Nothing was deleted. Superseded items are labeled, not removed.

---

## 1. Source list

There is **no single exported ChatGPT/Claude transcript file** committed in the repo. The
"chat-history material" exists as three corpora, all treated here as **evidence, not authority**:

**A. Live agent/chat transcripts (session history)**
- Cursor/Claude agent transcripts for this project (governance, MMI build, adversarial
  hardening sessions). `RESEARCH_INPUT` / `NEEDS_MMI_REVIEW` — transcripts are reasoning
  trails, never authority on their own.

**B. Repo artifacts that captured prior chat sessions** (ChatGPT research, Claude design,
Gemini cross-check, Grok audit). These are the durable residue of chat history:
- `VISION.md` — long-arc thesis in Matt's words (from chat). `AUTHORITATIVE_CURRENT`.
- `PROJECT_HANDSHAKE.md`, `CURRENT_STATE_MAP.md`, `MASTER_INDEX.md`, `PROGRESS.md`,
  `PROJECT_ACTIVITY_LOG.md`, `decision_cycles_log.md`, `AGENTS.md`, `PROJECT_GUARDRAILS.md`.
- `agent_concepts/` (SPARK maps, design tree, 70-agent scoreboard).
- `4. Product_Roadmap/` (concept docs, `_*_SPARK.md` idea captures, deep dives, contracts).
- `Research/`, `4. Product_Roadmap/Research_Inputs/` (ChatGPT/Gemini research packets).
- `3. SwarmCommand_Engine/.../Runtime_Implementation/` (built code + tests).
- `mmi/` (governance center — eight files + this intake folder).
- Legacy: `Unified Folder Structure - NorthStar + SwarmCommand Venture.md` (+ `.rd.md`),
  `NorthStar Certification + Licensing + Partner Ecosystem/`,
  `AI_Phishing_Simulation_Business/Inbox_Shield/`, `*_ARCHIVE_*.md`, `* - Copy.*` files.

**C. Windows consolidated ChatGPT master (secondary — not primary authority)**
- `/mnt/c/Unified Folder Structure NorthStar + SwarmCommand Venture/chat_history/MMI_CHATGPT_HISTORY_INTAKE_MASTER.md`
- Deduped merge of 13 ChatGPT intake drafts (10 unique). Indexed in
  `MMI_CHATGPT_HISTORY_MASTER_INDEX.md`. `RESEARCH_INPUT` — many hashes unverified.

> **Note:** The full repo index is large (200+ markdown/code artifacts). This intake
> classifies by *theme and authority tier*, with named examples, rather than enumerating
> every file. Section 10 lists what still needs a direct repo verification.

---

## 2. Current product thesis items

| Item | Evidence | Classification |
|---|---|---|
| Self-evolving, trigger-based multi-agent cyber-defense swarm; operator kill-switch always wins | `VISION.md` Thesis + Non-Negotiables | `AUTHORITATIVE_CURRENT` |
| Stage A → B → C arc (Analyze+Recommend → Auto-defend → Self-evolving swarm) | `VISION.md` Stage table | `AUTHORITATIVE_CURRENT` |
| Wedge product: email fraud / inbox-layer MDR for SMBs via MSPs (Stage A) | `PROJECT_HANDSHAKE.md` "Current Active Build Track" | `AUTHORITATIVE_CURRENT` |
| #1 target = full 70-agent governed blue-team swarm (not reducible) | `PROJECT_HANDSHAKE.md` Operator #1 Target | `AUTHORITATIVE_CURRENT` |
| Seven Non-Negotiables (kill switch, audit, reversibility, tenant isolation, signed promotion, human review of suspicious updates, operator approval of client-facing actions) | `VISION.md` Non-Negotiables | `AUTHORITATIVE_CURRENT` |
| Cyber-insurance evidence package as the funding/proof track | `PROJECT_HANDSHAKE.md`; Cyber Insurance specs | `SUPPORTED_BY_REPO` |

---

## 3. Architecture items

| Item | Evidence | Classification |
|---|---|---|
| SwarmCommand Agent Loop Runtime (orchestrator, blackboard, Commander case loop) | `3. SwarmCommand_Engine/.../core/` | `SUPPORTED_BY_REPO` / `BUILT_NEEDS_VERIFICATION` |
| 6-layer / 10-team agentic evidence swarm design | `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` | `AUTHORITATIVE_CURRENT` (design canon) |
| 70-agent SPARK inventory | `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` | `SUPPORTED_BY_REPO` (inventory-only per §7.0) |
| 70-agent scoreboard (Build Sequencer) | `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` | `AUTHORITATIVE_CURRENT` (build status source) |
| Agent Design Contract Template (§11 signed) | `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` | `AUTHORITATIVE_CURRENT` |
| Control plane: Mode Controller (#92), BRC (#89), Safe-Stop (#94), Privacy Filter (#93), Collective Immune System (#95), Cortex/Immune Interface (#96), Memory Consolidation/TBI (#97) | `mmi/MMI_GATE_REGISTRY.md` (all GATED) | `BUILT_NEEDS_VERIFICATION` → see §10 |
| Dual-LLM architectural law (actor never reads raw email; reader holds no tools) | `Dual_LLM_Contract.md` (referenced) | `SIGNED_BUT_UNBUILT` / `SUPPORTED_BY_REPO` — verify build depth |
| Shadow Watcher Swarm (10-layer contract; Layer 1 gated) | `PROJECT_HANDSHAKE.md`; Shadow Watcher contract | `SUPPORTED_BY_REPO` (Layer 1) / `SIGNED_BUT_UNBUILT` (Layers 2-10) |
| Specialisation Fission / Load Fission (#90/#91 gated) | `PROJECT_HANDSHAKE.md` | `SUPPORTED_BY_REPO` |

---

## 4. Governance / MMI items

| Item | Evidence | Classification |
|---|---|---|
| MMI governance center (8 files) | `mmi/MMI_PROTOCOL.md` … `MMI_HEALTH_STATE.md` | `AUTHORITATIVE_CURRENT` (docs/governance only) |
| MMI gate registry (component/gate status) | `mmi/MMI_GATE_REGISTRY.md` | `AUTHORITATIVE_CURRENT` |
| MMI decision log | `mmi/MMI_DECISION_LOG.md` | `AUTHORITATIVE_CURRENT` |
| MMI dispatcher script (scoreboard-derived; `--sync`, `--verify`, `MODE: ALL_CLEAR`) | Committed `scripts/mmi_dispatch.py` | `SUPPORTED_BY_REPO` (executable Stage 1 tool) |
| Proposed dispatcher lane-selection changes (Codex BUILD/REVIEW, auto-sync) | Session history only — see `MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md` | `NEEDS_MMI_REVIEW` / `BUILT_NEEDS_VERIFICATION` — **not accepted authority** |
| `MMI_CURRENT_STATE.md` (routing block derived; prose human-context) | repo root | `AUTHORITATIVE_CURRENT` routing block when in sync; prose is mixed (see §9) |
| Drift detector / build-truth verifier | `scripts/detect_drift.py`, `scripts/verify_build_truth.py` | `SUPPORTED_BY_REPO` |
| Grok completion gate | `audit_tools/complete_gate.py` | `SUPPORTED_BY_REPO` |
| AGENTS.md governance rules (Butterfly Hard-Stop §7.1, decision presentation §3.1, partner lanes §2.1, §2.2 routing) | `AGENTS.md` | `AUTHORITATIVE_CURRENT` |
| Next-Action Decision Rubric (§11 signed) | `decision_cycles_log.md` + rubric | `AUTHORITATIVE_CURRENT` |
| `DECISION_PROTOCOL.md` | repo root | `NEEDS_MMI_REVIEW` (logged as TRIAL, "not yet adopted into AGENTS.md authority") |
| MMI runtime integration / automation (vs file-based dispatcher) | `PROJECT_HANDSHAKE.md` anchor | `CONTRADICTION` risk — handshake says NOT active; committed dispatcher script exists |
| History intake folder | `mmi/history_intake/` | `RESEARCH_INPUT` — evidence maps only; see `README.md` |

---

## 5. Detection / evidence items

| Item | Evidence | Classification |
|---|---|---|
| Layer-1 detector agents promoted to GOVERNED_AGENT @ Evidence Stage 1 (#6 Header, #6A Email Auth, #8 Ghost Thread, #10 Lookalike, #24 MFA, etc.) | `core/orchestrator/*_agent.py` + tests | `BUILT_NEEDS_VERIFICATION` → §10 |
| Layer-5 Aggregate Challenge Pass + Aggregate Corroboration Agent | `core/...` + Layer 5 deep dive | `SUPPORTED_BY_REPO` |
| ReconciliationAgent ensemble (#84) | runtime code; #100 adversarial accepted | `BUILT_NEEDS_VERIFICATION` |
| Cyber Insurance Evidence Package (§11/§13 signed; gate library + generator Pass 1; §14 runner PASS) | `core/evidence_package/`, `audit_outputs/cyber_insurance_*` | `SUPPORTED_BY_REPO` (internal/synthetic only) |
| Client-Facing 5-Axis Email Scoring Rubric | `core/scoring/client_facing_rubric.py` + deep dive | `SUPPORTED_BY_REPO` |
| Adversarial suites #98–#102 (Privacy Filter, Mode Controller, Recon, BRC, Safe-Stop) | `mmi/MMI_GATE_REGISTRY.md` (ACCEPTED/HARDENED) | `AUTHORITATIVE_CURRENT` (status) |
| Runtime Instrumentation (RT) | `instrumentation/runtime.py`; accepted | `SUPPORTED_BY_REPO` |
| D9 calibration plan (synthetic-only) | `Mutant_Monkey_Package_Auditor_D9_Calibration_Plan.md` | `SUPPORTED_BY_REPO` (plan; not a runner) |

---

## 6. Research items

| Item | Evidence | Classification |
|---|---|---|
| Cyber-insurance evidence pain-points / synthesis / record-set research | `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_*` | `RESEARCH_INPUT` |
| Testing plan V1, scoring schema, scoring-correction evidence briefs | `Research/queries/*`, `Research_Inputs/Testing_*` | `RESEARCH_INPUT` |
| Competitive landscape / positioning | `6. Internal_Strategy/Competitive_Intel/competitive-landscape.md` | `RESEARCH_INPUT` |
| Lookalike / Executive-Impersonation deep dives | `4. Product_Roadmap/*_Deep_Dive.md` | `RESEARCH_INPUT` / `SUPPORTED_BY_REPO` (where built) |
| `Frontier_Intake_Log.md`, `THREAT_INTEL_LOG.md`, `think_sheet.md` | repo root | `RESEARCH_INPUT` |
| Gemini briefing | `MUTANT_MONKEY_GEMINI_BRIEFING.md` | `RESEARCH_INPUT` |

---

## 7. Concept ideas

| Item | Evidence | Classification |
|---|---|---|
| Builder Radar (dual-LLM market intel) | `4. Product_Roadmap/Builder_Radar_Concept_Doc.md` (CONCEPT, untracked) | `CONCEPT_IDEA` + `PARKED_DRAFT` |
| Mutant Monkey Radar (full pipeline) | `4. Product_Roadmap/Mutant_Monkey_Radar_Concept_Doc.md` (CONCEPT, untracked) | `CONCEPT_IDEA` + `PARKED_DRAFT` |
| Honeypot / Deception Layer | `4. Product_Roadmap/Honeypot_Deception_Concept_Doc.md` (CONCEPT, untracked; legal/consent gate) | `CONCEPT_IDEA` + `PARKED_DRAFT` |
| Purple Team Attacker Cost Doctrine | `4. Product_Roadmap/Purple_Team_Attacker_Cost_Doctrine.md` (CONCEPT, untracked) | `CONCEPT_IDEA` + `PARKED_DRAFT` |
| Threat Intelligence Daemon (concept + design contract) | `4. Product_Roadmap/Threat_Intelligence_Daemon_*` | `CONCEPT_IDEA` / `SIGNED_BUT_UNBUILT` — verify contract sign state |
| `_SPARK_*` idea captures (Cross-Channel Fraud Shield, SPARK Bibles, Eval Harness, Strategy Matrix, Railbridge Post-Invoice) | `4. Product_Roadmap/_*_SPARK*.md` | `CONCEPT_IDEA` |
| Tiered Detection Intensity, Two-Channel Confirmation, Vendor Baseline Store deep dives | `4. Product_Roadmap/*_Deep_Dive.md` | `CONCEPT_IDEA` / `RESEARCH_INPUT` |

> All four untracked concept docs are dated **June 14 2026**, marked **"CONCEPT — advisory
> lane only. No build authorization. Contract required before build."** They reference signed
> companions (Shadow Watcher Swarm, Dual LLM, Specialisation Fission). They must **not** be
> promoted by this intake.

---

## 8. Superseded NorthStar / SwarmCommand references

> **Important nuance (per the rebrand decision):** Per
> `4. Product_Roadmap/_Rebrand_to_Mutant_Monkey_Security_Consequence_Matrix.md` **Outcome =
> Option B** (Matt, 2026-06-04): "Mutant Monkey Security" is the **external/buyer-facing
> brand**; **"NorthStar" / "SwarmCommand" remain valid INTERNAL repo codenames** (code
> namespaces, repo paths, internal docs). So NorthStar/SwarmCommand **as internal codenames
> are NOT superseded** — only specific *buyer-facing product framings* are.

| Item | Evidence | Classification |
|---|---|---|
| "NorthStar Inbox Shield" as a **buyer-facing** product name | Cyber Insurance §13: buyer surfaces now say "Mutant Monkey Inbox Shield"; "NorthStar Inbox Shield" = internal codename | `SUPERSEDED` (buyer-facing only) |
| `NorthStar Certification + Licensing + Partner Ecosystem/` (cert program, licensing, partner portal) | dormant business-model expansion folder | `PARKED_DRAFT` / `NEEDS_MMI_REVIEW` (not in current Stage-A build track) |
| `AI_Phishing_Simulation_Business/Inbox_Shield/` (LangGraph demo, freelance revenue kit, `run_demo.ps1`) | early-era prototype/business artifacts | `SUPERSEDED` / `DO_NOT_USE` as architecture (pre-SwarmCommand-runtime) |
| `Unified Folder Structure - NorthStar + SwarmCommand Venture.md` (+ `.rd.md`) | older folder-layout planning | `SUPERSEDED` (repo structure has since evolved) |
| Windows master path `/mnt/c/.../Unified Folder Structure ...` as primary | `PROJECT_HANDSHAKE.md`: WSL repo is PRIMARY (2026-06-13); Windows = secondary/reference | `SUPERSEDED` (Windows-primary framing) |
| `*_ARCHIVE_*.md`, `* - Copy.*`, `THIRTY_DAY_PLAN - Copy.md`, `IDEA_PARKING_LOT - Copy.doc` | explicit archives/duplicates | `SUPERSEDED` / `DUPLICATE` |
| "NorthStar" namespace in code (`SwarmCommand_Engine/`, `northstar` repo root) | per Option B | `SUPPORTED_BY_REPO` (valid internal codename — **NOT** superseded) |
| VISION.md title "NorthStar + SwarmCommand — Vision" | internal codename usage | `AUTHORITATIVE_CURRENT` (content current; title is codename, not stale) |

---

## 9. Contradictions or drift risks

| # | Risk | Evidence | Classification |
|---|---|---|---|
| 1 | **`PROJECT_HANDSHAKE.md` current-state block is stale.** Top block reads "as of 50b58a8 … 2026-06-13" and its STATE/NEXT ACTION predate the #99–#102 adversarial hardening and the MMI ALL_CLEAR state. Current HEAD is well past 50b58a8. | `PROJECT_HANDSHAKE.md` lines 6, 17, 67 vs. `mmi/MMI_GATE_REGISTRY.md` / dispatcher ALL_CLEAR | `CONTRADICTION` / drift — **report only; do not patch in this phase** |
| 2 | **Multiple "current state" files** (`PROJECT_HANDSHAKE.md`, `CURRENT_STATE_MAP.md`, `MMI_CURRENT_STATE.md`, `mmi/MMI_HEALTH_STATE.md`, scoreboard) can disagree. MMI authority is now the gate registry + decision log + dispatcher `--verify`. | repo root + `mmi/` | `CONTRADICTION` risk — authority precedence should be documented |
| 3 | **"5-axis rubric" name is overloaded** (client-facing email rubric vs. think_sheet idea-scoring vs. Shadow Watcher eval matrix). | `PROJECT_HANDSHAKE.md` "NAMING CLARIFICATION" | `CONTRADICTION` (naming) — already flagged in handshake |
| 4 | **Untracked concept drafts** (the four June-14 docs) sit beside tracked roadmap files; a future session could mistake them for authorized. | `git status` (untracked) | drift risk — `PARKED_DRAFT`, already disclaimed in-file |
| 5 | **Project rename PARKED** but "Mutant Monkey" appears on buyer surfaces and new concept docs; internal "NorthStar" persists. Dual-name state is intentional (Option B) but is a standing low-grade confusion source. | rebrand consequence matrix Outcome | `NEEDS_MMI_REVIEW` (documented, intentional) |
| 6 | **D10 market proof OVERRIDDEN, not met** (signed operator override on cyber-insurance package). | `PROJECT_HANDSHAKE.md` cyber-insurance bullet | `NEEDS_MMI_REVIEW` (known override; not a defect) |
| 7 | **Intake vs dispatcher authority bleed** — routing code changes must not ship in the same pass as history classification. | `mmi/history_intake/README.md` separation rule | `GOVERNANCE/MMI ITEM` — enforced 2026-06-16 |
| 8 | **Windows ChatGPT master vs repo intake** — two classification surfaces; master has unverified hashes. | Master index + repo intake | `DUPLICATE` risk — master is secondary only |
| 9 | **Claude/Cursor "Authoritative System Compendium"** — title overclaims; body is research until verified. | `MMI_CLAUDE_CURSOR_HISTORY_INTAKE.md` | `CONTRADICTION` / `DO_NOT_USE` as authority label |

---

## 10. Items that need repo verification

These claims are asserted in governance docs but should be confirmed against live code/tests
before being treated as built truth (run `scripts/verify_build_truth.py` + targeted reads):

- Control-plane components #92/#89/#94/#93/#95/#96/#97 marked GATED — confirm code + gate
  artifacts still present at current HEAD.
- "1740 tests passing / 1 skipped / 49 xfailed" baseline (verified 2026-06-12) — re-run to
  confirm still green at current HEAD.
- Detector agents promoted to `GOVERNED_AGENT` @ Stage 1 (#6, #6A, #8, #10, #24, …) —
  confirm each has spec + agent module + test suite.
- Dual LLM: contract signed vs. "pattern GATED (696ee45)" — confirm built scope vs. contract scope.
- Shadow Watcher Swarm: Layer 1 GATED claim vs. Layers 2–10 unbuilt — confirm boundary.
- Threat Intelligence Daemon: concept doc vs. design contract — confirm whether §11 signed.
- `audit_outputs/` adversarial evidence files referenced in `mmi/MMI_DECISION_LOG.md` —
  confirm files exist at the cited commits.

---

## 11. Items that may be golden but require MMI review

High-potential ideas surfaced in chat history; **not authorized**, flagged for Matt/MMI review:

- **Purple Team Attacker Cost Doctrine** — coherent defensive-friction strategy tying
  Specialisation Fission pairs to attacker-cost outcomes; could anchor a differentiated moat.
- **Honeypot / Deception Layer** — high strategic value but gated behind PIPEDA/jurisdiction/
  consent/liability legal review; do not contract before legal answers exist.
- **Builder Radar + Mutant Monkey Radar** — dual-LLM competitive/market-intel memory; useful,
  but open question of repo placement and source allowlist; potential overlap (see §12).
- **Cross-Channel Fraud Shield SPARK** — extends the wedge beyond email; needs scoping.
- **DECISION_PROTOCOL.md** — promising decision-routing model still in TRIAL, not adopted
  into AGENTS.md authority; review for adoption or retirement.
- **70-agent breadth runway** — many detector functions exist as wrap candidates; the
  "what's next" engine (Action C) is described as complete; confirm and leverage.

---

## 12. Items that must not become authority

- **All four untracked June-14 concept docs** (Builder Radar, Mutant Monkey Radar, Honeypot,
  Purple Team) — `CONCEPT_IDEA` / `PARKED_DRAFT`. Self-disclaimed "authorizes nothing."
- **Illustrative/sample content** — e.g. honeypot "fake surfaces (examples — not authorized,
  illustrative only)"; `AI_Phishing_Simulation_Business/Inbox_Shield/samples/ceo_wire_fraud.txt`
  and demo outputs — `DO_NOT_USE` as architecture or product truth.
- **Archives & copies** — `*_ARCHIVE_*.md`, `* - Copy.*` — `SUPERSEDED`/`DUPLICATE`; history only.
- **Agent transcripts / chat logs** — reasoning trails only; never authority by themselves.
- **`SPARK` idea captures** — brainstorming tier; not specs.
- **`think_sheet.md` strategic rubric** — idea-prioritization scratchpad; not a signed rubric.
- **This intake file itself** — `NON-AUTHORITATIVE`. Classifications here are an MMI map, not
  a decision. Authority remains the gate registry, decision log, and `mmi_dispatch.py --verify`.

---

## Final rule

This report **does not authorize build, research, design, or promotion**. It classifies
chat-history material so Matt can see the full idea-map in one place. **Matt must explicitly
authorize any next phase** (BUILD / RESEARCH / DESIGN / continued HOLD) after reviewing this
classified intake. Any item moved out of `CONCEPT_IDEA` / `PARKED_DRAFT` / `NEEDS_MMI_REVIEW`
requires a separate, explicit operator authorization and (for build) a §11-signed contract.
