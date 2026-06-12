# Phase 3 — Detection Swarm Contract — Amendment 1
## Canonical `sender_domain` + scoped TokenUsageTracker attribution

**Document type:** Contract Amendment (pre-§11)
**Status:** §11 SIGNED — Matt Nichol June 11th 2026. Build authorization granted per amendment scope.
**Date drafted:** June 11, 2026
**Drafted by:** Cursor (execution lane), transcribing operator-settled substance from the 2026-06-10 session per the agreed model (advisory/operator designs → execution lane writes to disk). Signature reserved for the operator.
**Amends:** `4. Product_Roadmap/Phase3_Detection_Swarm_Agent_Design_Contract.md` (§11 SIGNED 2026-06-10, committed `c522292`)
**Authority:** Matt Nichol — sole signing authority

---

## §A — Purpose

Phase 4 (ReconciliationAgent) must correlate evidence across detection agents by sender domain. The signed §3 schemas have **no shared domain key**, so there is nothing to join on. Because no Phase 3 agent is built yet, adding the key now means it is built in correctly on day one — **no migration, no dual-write, no backfill.** This amendment also clarifies which agents must attribute token cost, so the Attacker Cost Model is not applied to lookup-only agents that consume no tokens.

---

## §B — Schema additions (amends §3.1 and §3.2)

Add one field, `sender_domain: str`, to both agents:

- **§3.1 SenderHistoryAgent** (`sender_signal`): add `sender_domain` — the normalized canonical sender domain.
- **§3.2 GeoVelocityAgent** (`geo_signal`): add `sender_domain` — the same normalized value; this is the join key Phase 4 uses to correlate the two contributions for one `email_id`.

This is an **additive** field only. No other §3 schema changes. No verdict field is introduced (P3-D1 unchanged); evidence-type closure (P3-D2) is unchanged except for this one additive key on these two agents.

### Canonical normalization rule (applied before any write of `sender_domain`)

In order:
1. Strip surrounding whitespace.
2. Strip a single trailing dot (root label): `example.com.` → `example.com`.
3. Strip a `:port` suffix if present: `mail.example.com:443` → `mail.example.com`.
4. Lowercase ASCII (DNS names are case-insensitive).
5. IDNA encode (UTS-46) to the ASCII A-label / punycode form for internationalized domains.

Result: `Example.COM.`, `EXAMPLE.com` → `example.com`; `MÜNICH.de` → `xn--mnich-kva.de`. The **full host is preserved** (subdomains kept; not reduced to the registrable domain). Both agents MUST use the identical normalization helper so the values are byte-identical for correlation.

---

## §C — TokenUsageTracker attribution scope (clarifies P3-D5 / §4 Attacker Cost Model)

- **Tenant isolation is unchanged and universal:** every blackboard write from **all six** agents includes `tenant_id`, and reads filter by `tenant_id` (P3-D5). This stands as already signed.
- The **`TokenUsageTracker.record(tenant_id, ...)` attribution requirement applies ONLY to the token/LLM-consuming detection agents: `ContentAnalyzer` (§3.3) and `AttachmentSandbox` (§3.5).** On any run where these agents consume model tokens, the usage MUST be recorded against the agent's own `tenant_id`.
- The lookup-only agents — `SenderHistoryAgent`, `GeoVelocityAgent`, `URLReceptor`, `ImageClassifier` — are **not** required to call `TokenUsageTracker`, because they perform history/IP/URL/image lookups, not model-token calls. If any of them later consumes model tokens, the same per-tenant attribution rule applies to it from that point.
- **Rationale:** mandating a `TokenUsageTracker.record` call on every run of a non-token agent would be a false requirement and would make the gate assert behaviour that does not exist.

---

## §D — Test requirements (amends §5)

- **#78 / #79:** Class 1 and Class 2 must assert `sender_domain` is present and correctly normalized — lowercase, no trailing dot, no port, punycode for IDNs — including dedicated normalization unit tests over adversarial inputs (`Example.COM.`, `host:443`, IDN).
- **ContentAnalyzer / AttachmentSandbox:** Class 2 must assert `TokenUsageTracker.record` is called with the agent's own `tenant_id` on a token-consuming run.
- **All six:** Class 2 must assert `tenant_id` is present on every blackboard write (reaffirms P3-D5).

---

## §E — What this amendment does NOT change

- No change to: verdict prohibition (P3-D1), evidence-type closure beyond the one additive key (P3-D2), Layer 0 mandatory briefing (P3-D3), cloud-side-only execution (P3-D4), ELITE 85+ gate (P3-D6), ES2 build target (P3-D8), Linux path `core/detectors/` (P3-D9).
- No new `core/` namespace beyond the contract's `core/detectors/`.
- The MutationEngine proprietary-capability-rubric clause is **NOT** added here — per the 2026-06-10 operator call it belongs in the Phase 5 contract, not Phase 3.

---

## §F — Scoreboard impact

None at signing. Rows #78-83 remain `SIGNED_UNBUILT`; each flips to `GOVERNED_AGENT` as it is built, tested (three classes), and gate-clean under the amended schemas.

---

## §11 — Operator Sign-Off

**Status:** §11 SIGNED — build authorization granted per amendment scope.

**Signed:** Matt Nichol
**Date:** June 11th 2026
