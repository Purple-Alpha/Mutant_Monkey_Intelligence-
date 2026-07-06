# MMI Chaos Doctrine — Break to Heal

**Status:** ACTIVE DOCTRINE  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-01  
**Build Rule #1:** `architecture/MMI_BUILD_RULE_01_OUTSIDE_THE_BOX_2026-07.md`

---

## Matt directive (verbatim intent)

**For chaos testing we are doing chaos testing to make stuff snap and break — not to play inside another set of rules and laws.**

**We need to break stuff or we will never heal stuff.**

---

## What this is NOT

| Fake chaos | Real chaos (MMI) |
|------------|------------------|
| Validation testing with extra checklists | Corruption, contradiction, stale state, hostile input |
| "PASS if gates hold" | **SUCCESS if snap is detected, contained, evidenced, healed** |
| Staged fixtures that never mutate | Isolated clone that **is allowed to break** |
| Another layer of compliance laws | Destruction in the lab → immune memory in the brain |
| Afraid to corrupt `tasks.json` in a test | **Intentionally** corrupt clone `tasks.json` and watch what lies |

Weapon concept §3: *If a test never creates corruption, contradiction, stale state, hostile input, replay pressure, missing evidence, overloaded state, or a recovery requirement — it is not chaos testing. It is only validation testing.*

---

## The rule

```text
Destroy the clone, not the brain.
Break → observe snap → preserve evidence → heal → harden → break again.
```

No healing without a real snap. No snap without permission to break the clone.

---

## Where breaking happens

| Zone | Break allowed? |
|------|----------------|
| **Authority repo** (`/mnt/c/MMI` live) | **NO** — brain |
| **Chaos lab clone** (Provisioner) | **YES** — battlefield |
| **B2 / latest-good** | **NO** — DNA (read for rebuild proof) |

---

## Success condition

A chaos run succeeds when:

1. Something **actually broke** (or provably resisted break — with evidence)
2. Snap surface is **named** (what lied, what corrupted, what overloaded)
3. Authority repo **unchanged** (fingerprint proof)
4. Evidence packet exists for human-reviewed hardening
5. Clone destroyed or rebuilt for next smash

---

## Next execution component

**Chaos Lab Provisioner** — creates the isolated clone where breaking is legal.

Spec: `chaos/MMI_CHAOS_LAB_PROVISIONER_SPEC_2026-07.md`  
Runner: `scripts/chaos_lab_provisioner.py`

Then: Mirror Dimension Router → wire tarpit → mesh smash → 48h proof.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Break-to-heal doctrine filed |
