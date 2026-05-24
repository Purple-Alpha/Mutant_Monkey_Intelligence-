# NorthStar SwarmCommand — 12-Week Timeline (Annotated)

**Source:** Forward-looking 12-week build plan provided by Matt on 2026-05-20.

**This document records the timeline verbatim, with status annotations for each
item.** It is not the build queue — for the live build queue see
`PROJECT_HANDSHAKE.md` and the "Next priority order" section of this file.

**Status legend:**
- ✅ Done — code on disk, tests passing.
- 🟡 Partial — some of the intent is built; gap noted.
- 🟦 Specced — Definition-of-Done document exists; code not yet written.
- ❌ Not built — no spec, no code.

---

## Week 1–2: Foundation

| Item | Status | Notes |
|---|---|---|
| Email Ingest Path (`normalize_raw_email`, `EmailInboundPayload`, `BlackboardRecord`) | ✅ | `core/ingest/email_ingest_agent.py`. `EmailInboundPayload` is the locked record; `BlackboardRecord` is the envelope. |
| Error Discipline (`EmailIngestError`, `ValidationError`) | ✅ | `EmailIngestError(ValueError)` for ingest-side normalization failures; strict `pydantic.ValidationError` for schema. |
| Blackboard Engine — structured | ✅ | `core/blackboard/`. 13 locked record types, append-only JSONL storage. |
| Blackboard Engine — vector | ❌ | No vector store yet. Pure JSONL. Adding embeddings + semantic search is a separate mission. |
| Agent Registry | ✅ | `core/orchestrator/registry.py`. 11 registered agents at time of writing. |
| Universal Prompt Architecture | 🟡 | `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` locked verbatim in code. Daily digest prompt is a placeholder. No formal architecture doc describing prompt-versioning and locked-string conventions. |
| JSON Communication Protocol | 🟡 | Implemented via strict pydantic payloads on every Blackboard record. No standalone protocol spec; the schema *is* the protocol. |
| Governance Constitution | ✅ | `Governance_Constitution/governance-constitution-loop.md` + 11 numbered `PROJECT_GUARDRAILS.md` items. |
| Tenant-Bound Swarm Model | 🟦 | DoD spec landed at `Policy_Pipeline/multi-tenant-isolation-hardening.md`. Phase 2 code (signed `target_production_tenant_id`, per-tenant sandbox routing, gate rejection of mismatches) pending. |

---

## Week 3–5: Swarm Runtime

| Item | Status | Notes |
|---|---|---|
| Dynamic Scaling Engine (MAPE-K) | ❌ | Not built. Monitor / Analyze / Plan / Execute over a shared Knowledge surface is absent; cycles run on demand. |
| Agent Execution Loop | ✅ | `core/production/loop.py` (Blue-only) + `core/sandbox/loop.py` (Red/Blue). |
| Orchestrator Layer | ✅ | `core/orchestrator/{routes.py,registry.py}`. All Blackboard writes go through one governed path. |
| Detection Layer | ✅ | Basic deterministic prototype in `core/production/loop.py::_detect`. Real LLM detector is a future swap. |
| Scoring Layer | ✅ | `risk_scoring_001` + Inbox Shield `email_risk_scoring_001` (`core/scoring/email_risk_scoring_agent.py`). |
| Workflow Layer | ✅ | `workflow_trigger` records routed by `orchestrator_001`; consumers include `policy_consumer.py` and the future digest send path. |
| Drafting Layer | ✅ | `daily_digest_001` (`core/drafting/daily_digest_agent.py`). Other drafting agents specced under `3. SwarmCommand_Engine/Agents/Drafting_Agents/`. |
| Audit Layer | ✅ | `audit_001` (operational telemetry) + `governance_001` (governance mutations). Boundary enforced by Guardrail 11. |
| Deterministic E2E Smoke Tests | ✅ | `tests/test_e2e_inbox_shield_smoke.py` (6 tests). Full audit chain + idempotency + production-loop integration. |

---

## Week 6–8: Sandbox Training Pit

| Item | Status | Notes |
|---|---|---|
| Red Swarm (synthetic phishing generators) | ✅ | `red_sandbox_001` writes `SYNTHETIC_ATTACK_CASE` records inside sandbox only. Red agents are sandbox-only by registry enforcement. |
| Blue Training Swarm | ✅ | Sandbox `_blue_detect` in `core/sandbox/loop.py` evaluates synthetic Red cases. |
| Sandbox Blackboard | ✅ | `Environment.SANDBOX` partitioning of the JSONL Blackboard. Red→Blue→audit chain runs inside sandbox. |
| Simulation Loop | ✅ | `run_sandbox_cycle` (`core/sandbox/loop.py`). |
| Mutation Engine | ✅ | `core/mutation/engine.py`. Emits signed `policy_update` candidates only when promotion rules pass. |
| Evolution Evaluator | ✅ | `MutantEvaluationPayload` + the mutation engine's compare-vs-baseline path. |

---

## Week 9–10: Policy Update Pipeline

| Item | Status | Notes |
|---|---|---|
| Policy Signing | ✅ | `core/policy/signing.py`. HMAC-SHA256 over the canonical payload + signer identity. |
| Policy Promotion | ✅ | `core/policy/pipeline.py`. Signature re-verification, cross-boundary re-audit, idempotent promotion. |
| Rollback System | ✅ | `core/policy/rollback.py` (sandbox-signed reverts) + alert subscriber + regression detector (automated rollback trigger). |
| Audit Trail | ✅ | Closed audit chain from boundary `audit_verdict` → workflow trigger → `policy_applied` → `policy_regression_alert`. Re-verified at the Guardrail 11 gate before any production_state mutation. |

---

## Week 11–12: Deployment

| Item | Status | Notes |
|---|---|---|
| Tenant Swarm Launcher | ❌ | Not built. One-command "bring up an isolated swarm for tenant X" needs multi-tenant isolation Phase 2 to land first. |
| Tenant Isolation Layer | 🟦 | Same `multi-tenant-isolation-hardening.md` spec as the Week 1–2 item. Phase 2 code is the unblocker for the launcher. |
| Monitoring Dashboard | ❌ | Read-only UI over the Blackboard + `production_state`. Backend reads are already trivial; UI is the work. |
| Incident Timeline Generator | ❌ | Replays the audit chain for one incident into a human-readable timeline. Builds entirely on existing records. |

---

## Forward queue (the real "next work")

Items still genuinely outstanding from this timeline, in roughly the order they should land:

1. **Operator Kill Switch (RSI prereq #7)** — not on this timeline but in queue. DoD spec approved 2026-05-20 at `Policy_Pipeline/operator-kill-switch.md`. Smallest safety win; should land before any further deployment-tier work.
2. **Daily Digest Prompt locking** — placeholder still in `core/drafting/daily_digest_agent.py`. Trivial swap once Matt provides the locked text; unblocks real E2E testing of the drafting layer.
3. **Multi-tenant isolation Phase 2** — implement signed `target_production_tenant_id` + pipeline/gate rejection of mismatches. Unblocks tenant launcher and isolation layer.
4. **Vector Blackboard** — pick a vector store (Chroma / sqlite-vss / lancedb), embed per record, expose `find_similar_records(query, k)`. Mission-sized.
5. **Universal Prompt Architecture** — formal doc + (small) prompt-registry module if locked strings outgrow inline constants.
6. **JSON Communication Protocol** — formal doc. Mostly implemented; needs to be written down for downstream / external consumers.
7. **MAPE-K Dynamic Scaling Engine** — Monitor / Analyze / Plan / Execute loop above the existing cycles. Substantial mission; spec it first.
8. **Tenant Swarm Launcher** — depends on (3).
9. **Monitoring Dashboard** — read-only UI layer. UI choice (Next.js / Streamlit / FastAPI+HTMX) is its own decision.
10. **Incident Timeline Generator** — depends on standardized incident ids.

---

## See Also
- [`../3. SwarmCommand_Engine/Agent_Loop_Runtime/README.md`](../3.%20SwarmCommand_Engine/Agent_Loop_Runtime/README.md) — runtime state and current build target.
- [`../PROJECT_HANDSHAKE.md`](../PROJECT_HANDSHAKE.md) — live build queue and resume rule.
- [`../3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/multi-tenant-isolation-hardening.md`](../3.%20SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/multi-tenant-isolation-hardening.md) — DoD spec for the Tenant-Bound Swarm Model + Tenant Isolation Layer items.
- [`../3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/operator-kill-switch.md`](../3.%20SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/operator-kill-switch.md) — DoD spec for operator kill switch (RSI prereq #7).

---

**Last updated:** 2026-05-20
