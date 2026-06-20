# MMI Autonomous Brain — Stage 1 Doctrine-Only Gaps

**Status:** Tier 1 passive gap callout (F5). Documents what remains **doctrine-only** or **not enforced in code** after F1–F5 artifact creation.

**Normative source:** `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` §14

**Parent contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Updated:** Tier 1 build close (passive artifacts only; no runtime wiring).

---

## Gap table

| Capability | Tier 1 artifact status | Enforced in code? | Notes |
|---|---|---|---|
| BLOCK-on-conflict (authority BLOCK vs scoreboard/contracts) | Doctrine in F1 + review material §5 | **No** | `mmi_dispatch.py` does not auto-flag dispatcher vs scoreboard conflicts |
| Decision Audit Appendix live surface | Schema only (F4) | **No** | No appendix file or JSONL with decision history |
| `MMI_TASK_REGISTRY` mechanics | Schema only (F2) | **No** | No populated registry; no lifecycle writes |
| Registry-fed routing | Forbidden in F1/F2 | **No** | `collect_delegation_tasks()` unchanged |
| Auto-prompt generation | F3 template only | **No** | AUTH-4 not authorized |
| Contradiction tooling / automation | Manual flag doctrine only | **No** | AUTH-7 not authorized; Tier 1 flags operator-review only |
| Owner dashboard / brief | Not built | **No** | AUTH-6 not authorized |
| Autonomous task selection | Forbidden | **No** | AUTH-5 not authorized |
| Dispatcher edit (`AUTH-2-EDIT`) | Forbidden | **No** | `scripts/mmi_dispatch.py` untouched at Tier 1 |
| Always-on sync / hooks / daemons / watchers | Prohibited | **No** | No background `--sync` automation |
| MMI write automation (`AUTH-3B`) | Not authorized | **No** | Human MMI record updates only |
| `BUILD_AUTHORIZATION_IMPLIED` disarming | Doctrine (F1, review I13) | **Partial** | Dispatcher still emits field; operators must disarm mentally |

---

## What Tier 1 **did** add (passive only)

| Artifact | Role |
|---|---|
| F1 `MMI_REPO_SURFACE_REGISTRY.md` | Closed surface list + exclusions |
| F2 `MMI_TASK_REGISTRY_SCHEMA.md` | Schema-only; no live tasks |
| F3 `MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md` | Completion packet shape |
| F4 `MMI_DECISION_AUDIT_APPENDIX_SCHEMA.md` | Appendix record shape; examples in-doc only |
| F5 (this file) | Gap honesty |

**None of the above changes dispatcher output or runtime behavior.**

---

## Tier 2 / Tier 3 remain blocked until separate gates

| Tier | Requires | Not authorized by Tier 1 |
|---|---|---|
| Tier 2 tooling | Tier 1 stable + per-tool AUTH gate | AUTH-3B writes, AUTH-4 prompts, AUTH-7 contradiction tooling |
| Tier 3 autonomy | Tier 1 + Tier 2 + **standalone AUTH-5** | Autonomous MMI task selection |

AUTH-5 cannot be bundled with Tier 1 or Tier 2 in a single operator authorization.

---

## Operator rule

Prose in F1–F5 or review material does **not** imply runtime enforcement. Closing a gap requires explicit gate authorization, implementation slice, tests, and usually `MMI-DEC-*` + verify PASS.
