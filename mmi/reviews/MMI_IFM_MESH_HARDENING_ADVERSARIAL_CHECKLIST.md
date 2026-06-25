# MMI IFM Mesh Hardening — Adversarial Review Checklist

**Classification:** `ADVERSARIAL_REVIEW` · `AUDIT_ARTIFACT` · `PRE_IMPLEMENTATION` · `NOT_BUILD_AUTHORIZATION`

**Status:** Checklist **FILED** — ready for reviewer execution against signed contract; implementation tests **deferred until mesh build authorized**

**Authority anchor:** `docs/mmi/contracts/004_immune_federation_mesh_contract.md` (§11 MMI-DEC-140 · IFM-D1–D12) · `mmi/research/MMI_MESH_HARDENING_RESEARCH_CLOSEOUT_MMI-DEC-131.md` · `mmi/research/MMI_IFM_S13_KEY_EPOCH_ROTATION_RESOLUTION_MMI-DEC-140.md`

**Date filed:** 2026-06-25

**Boundary:** Adversarial test catalog only. Does not authorize mesh bus build, key management service, GOVERNED_AGENT promotion, or AUTH-5. Checklist items marked `UNTESTED` until a future build lane supplies runtime evidence. Reviewer PASS on design-only items means contract coverage confirmed — not production hardened.

---

## 1. How to use this checklist

1. **Design review (now):** Confirm each attack scenario is **explicitly blocked** by IFM-D* contract text or addendum. Mark `DESIGN_OK` or `GAP`.
2. **Build review (later):** Re-run with failing tests, packet captures, or gate output. Mark `PASS` / `FAIL` / `BLOCKED`.
3. **Evidence rule:** Per `mmi/MMI_AUDIT_REVIEW_TEMPLATE.md` — cite file path, commit hash, test name, or audit artifact ID. Prose alone is not evidence.

**Default pre-build posture:** all rows start `UNTESTED`.

---

## 2. Guardrail 11 — tenant truth never crosses (IFM-D9, IFM-D12)

| ID | Attack scenario | Expected outcome | Contract ref | Status |
|----|-----------------|------------------|--------------|--------|
| IFM-AUD-001 | Egress pulse includes raw email body fragment | Reject before bus publish; no partial redaction fallback | IFM-D9 B→A | UNTESTED |
| IFM-AUD-002 | Pulse carries subject line or vendor/customer name | Reject | IFM-D9, §3 prohibited list | UNTESTED |
| IFM-AUD-003 | Pulse carries mailbox identifier or user ID | Reject | IFM-D9 B | UNTESTED |
| IFM-AUD-004 | Pulse carries unredacted URL or domain (reversible) | Reject or HMAC-only fingerprint per IFM-D2 | IFM-D2, IFM-D9 | UNTESTED |
| IFM-AUD-005 | Pulse carries payment amount, account, or invoice number | Reject | IFM-D9 B | UNTESTED |
| IFM-AUD-006 | Pulse carries case timeline or analyst comment | Reject | IFM-D9 B | UNTESTED |
| IFM-AUD-007 | Receiving tenant API accepts Field-class B payload on bus channel | Reject at ingress schema gate | IFM-D9 | UNTESTED |
| IFM-AUD-008 | Audit-plane Field-class C (billing attribution) leaked onto bus | Reject; C never enters A | IFM-D9 | UNTESTED |
| IFM-AUD-009 | Cross-pool pulse implies peer can query origin evidence | No query path; local match only | IFM-D12, Guardrail 11 | UNTESTED |
| IFM-AUD-010 | MSP operator uses mesh visibility to inspect tenant inbox | Denied — mesh is sanitized alert propagation only | §3 doctrine | UNTESTED |

---

## 3. HMAC, key epoch, and privacy tags (IFM-D2, IFM-D4)

| ID | Attack scenario | Expected outcome | Contract ref | Status |
|----|-----------------|------------------|--------------|--------|
| IFM-AUD-011 | Plain SHA-256 on low-entropy indicator (known domain) | Reject; require HMAC-SHA256 | IFM-D2 | UNTESTED |
| IFM-AUD-012 | Dictionary attack against published fingerprint | No recovery of raw value without `mesh_epoch_key` | IFM-D2 | UNTESTED |
| IFM-AUD-013 | Tenant-local detection agent obtains `mesh_epoch_key` | Key unavailable to tenant agents | IFM-D2 | UNTESTED |
| IFM-AUD-014 | Global system-wide correlating salt for tenant tags | Rejected design — pool-scoped HMAC only | IFM-D4 | UNTESTED |
| IFM-AUD-015 | `source_tenant_tag` stable across 90+ day horizon | Non-linkable beyond detection window | IFM-D4 | UNTESTED |
| IFM-AUD-016 | Receiver correlates two tenants via shared tag across pools | Tags scoped per MSP mesh pool | IFM-D4 | UNTESTED |
| IFM-AUD-017 | Pulse signed with epoch N while receiver only holds N-2 (outside overlap) | Reject verify | §13 #3 overlap 14d | UNTESTED |
| IFM-AUD-018 | Pulse signed with retired epoch after overlap + retention window | Reject operational accept | §13 #3 90d retention | UNTESTED |
| IFM-AUD-019 | Pulse accepted during dual-verify overlap with prior epoch | Accept (current or immediately prior epoch) | §13 #3 | UNTESTED |
| IFM-AUD-020 | Emergency revoke: old epoch pulses after 24h sunset | Reject new operational accept | §13 #3 emergency | UNTESTED |
| IFM-AUD-021 | Agent-initiated emergency epoch revoke without Matt | Denied — Matt-only | §13 #3 §4 | UNTESTED |
| IFM-AUD-022 | Epoch rotation thrash (<7d minimum lifetime) | Reject or rate-limit epoch bump | §13 #3 min 7d | UNTESTED |
| IFM-AUD-023 | Raw indicator value retained after egress sign | Discarded before bus | IFM-D2 | UNTESTED |

---

## 4. Anti-poisoning and compute abuse (IFM-D3, IFM-D5, IFM-D10, IFM-D11)

| ID | Attack scenario | Expected outcome | Contract ref | Status |
|----|-----------------|------------------|--------------|--------|
| IFM-AUD-024 | Single weak signal triggers outbound pulse | Reject — need ≥2 signal families | IFM-D3 | UNTESTED |
| IFM-AUD-025 | Attacker floods mesh with LOW trust pulses | Receivers log-only or cheap match; no forced deep inhale | IFM-D11 | UNTESTED |
| IFM-AUD-026 | HIGH trust pulse forces peer Lung deep inflation without local confirm | Reject — `DEEP_LOCAL_INHALE_REQUIRES_LOCAL_CONFIRMATION` | IFM-D11, schema | UNTESTED |
| IFM-AUD-027 | Coordinated false pulses across pool trigger synchronized overreaction | Local rate limits + Mode Controller `#92` caps | IFM-D10, §8D | UNTESTED |
| IFM-AUD-028 | Mesh pulse bypasses local Token Usage Tracker `#71` attribution | Surge compute billed to inhaling tenant | IFM-D10, closeout §5 | UNTESTED |
| IFM-AUD-029 | RA `#84` signs raw evidence blob onto bus | Reject — sanitized envelope only | IFM-D5 | UNTESTED |
| IFM-AUD-030 | RA signature implies cross-tenant inspection authorization | Signature means sanitization pass only | IFM-D5 | UNTESTED |
| IFM-AUD-031 | Poisoned pattern pollutes global tenant memory | Patterns local-only; no shared brain | Guardrail 11 | UNTESTED |
| IFM-AUD-032 | Sustained poison campaign on active epoch | Triggers Matt-only emergency revoke path (design) | §13 #3 §4 | UNTESTED |
| IFM-AUD-033 | Numeric copy cap exceeded (when §13 #1 locked) | Local Safe-Stop; no unbounded inflation | IFM-D10, §13 #1 TBD | UNTESTED |

---

## 5. Replay, TTL, and clock skew (IFM-D6)

| ID | Attack scenario | Expected outcome | Contract ref | Status |
|----|-----------------|------------------|--------------|--------|
| IFM-AUD-034 | Replay duplicate `pulse_id` | Reject duplicate | IFM-D6, §6 | UNTESTED |
| IFM-AUD-035 | Pulse with `expires_at` in the past | Reject expired | IFM-D6 | UNTESTED |
| IFM-AUD-036 | LIGHT tier pulse retained >6h operational | Reject or archive non-operational | §6 TTL defaults | UNTESTED |
| IFM-AUD-037 | NORMAL tier pulse retained >24h operational | Reject or archive | §6 | UNTESTED |
| IFM-AUD-038 | DEEP tier pulse retained >72h operational | Reject or archive | §6 | UNTESTED |
| IFM-AUD-039 | `issued_at` skew +301s from receiver clock | Reject outside ±300s tolerance | §13 #3 skew | UNTESTED |
| IFM-AUD-040 | Replayed expired pulse re-triggers Lung inflation | Reject; replays non-operational | IFM-D6 | UNTESTED |
| IFM-AUD-041 | Archived audit pulse re-injected onto live bus | Reject — audit artifacts non-operational | §6 | UNTESTED |
| IFM-AUD-042 | Schema downgrade attack (`schema_version` rollback) | Reject unknown/old version at gateway | §9 schema | UNTESTED |

---

## 6. Consent, revocation, and Mode Controller (IFM-D7, `#92`)

| ID | Attack scenario | Expected outcome | Contract ref | Status |
|----|-----------------|------------------|--------------|--------|
| IFM-AUD-043 | Tenant in `MESH_DISABLED` emits pulse | Block egress | §7 | UNTESTED |
| IFM-AUD-044 | Tenant in `MESH_RECEIVE_ONLY` emits pulse | Block egress | §7 | UNTESTED |
| IFM-AUD-045 | Revoked tenant continues receiving pulses | Block inbound after revocation | §7 | UNTESTED |
| IFM-AUD-046 | Revocation deletes legally required audit logs | Audit retained; mesh I/O stopped only | §7 | UNTESTED |
| IFM-AUD-047 | MSP pool policy overrides tenant `MESH_DISABLED` | Denied — tenant boundary governs | §7, addendum §10 | UNTESTED |
| IFM-AUD-048 | `MESH_LOCAL_ONLY_DURING_INCIDENT` still accepts inbound during incident | Suspend mesh I/O per state | §7 | UNTESTED |

---

## 7. Review summary block (copy per execution)

```
Component: Immune Federation Mesh hardening (contract-only / pre-build)
Review date:
Reviewer:
Evidence files reviewed:
Claimed result:
Evidence strength: (file paths / git hashes / test counts present yes/no)
Blocking deviations:
Warnings:
Scope violations:
Decision: ACCEPT / REVISE / REJECT / PARK / VERIFY / ESCALATE
Reason:
Required follow-up:
Matt approval required:
```

---

## 8. Explicit non-authorization

This checklist does **not** authorize mesh implementation, pilot wiring, key service build, or §13 numeric lock-in beyond advisory memos. Passing design review does not substitute for future Grok/Gemini completion gate on runtime code.

**Next when build authorized:** map each `IFM-AUD-*` row to automated test or packet fixture; file gate output under `audit_outputs/ifm_mesh_*`.

---

**Filed by:** Cursor (AUDIT lane — Matt authorized audit session 2026-06-25)
