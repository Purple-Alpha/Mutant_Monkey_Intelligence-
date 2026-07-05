# MMI Control Envelope Cap Decision Worksheet

**Authority:** Matt (Super) — signed 2026-07-03  
**Decision:** `DEFAULT_PER_DAY_CAP = 8_000_000` tokens · `DEFAULT_PER_HOUR_CAP = 800_000` tokens  
**Status:** FROZEN in code + spec (not dollars — see §1)

---

## 1. Unit clarification (critical)

The control envelope accounts in **tokens** (`SPEND_UNIT = tokens`), not USD.

| If Matt meant | Tokens/day | Approx USD/day @ $15/M tokens (frontier API) |
|---------------|------------|-----------------------------------------------|
| **8M tokens/day** (correct reading) | 8,000,000 | ~$120/day |
| 5M tokens/day (Claude spec proposal) | 5,000,000 | ~$75/day |
| $8M USD/day (literal) | ~533B tokens @ AFE attacker rate | Not envelope-scoped — wrong unit |

Matt's intent matches **8 million tokens per day** — intelligence headroom for Full Matrix runs, with T1/T3 as kill switch.

---

## 2. Evidence on record (what we actually have)

| Evidence source | What it tells us | Confidence |
|-----------------|------------------|------------|
| **T1/T3 harness (built)** | Kill switch works **independent of cap magnitude** — tested at 100/hour; breach → SUSPENDED, runaway → HALTED | **HIGH** — falsifiable, on record |
| **Phase 1 stability (3× Tier 4)** | Full canonical stack completes without envelope wired — **no defender token ledger yet** | **N/A for cap sizing** |
| **Purple evasion per run** | 12 scenarios + mesh + iceberg per lab run — proxy complexity, not token count | **LOW for caps** |
| **Iceberg cryptolalia (~8.7 KB/run)** | Attacker-side bytes from one run — not defender LLM spend | **LOW for caps** |
| **`kinetic_telemetry.py` AFE** | Attacker economics @ $0.015/1K tokens — **display only, not enforcement** | **MEDIUM for economics framing** |
| **AGI Phase 3 §3** | Sustained **1:500 AFE ratio** over 30 days — needs headroom but bounded | **MEDIUM** — future gate |
| **Matrix §6 M4** | 48h continuous assault — upper bound stress test | **MEDIUM** — not built |
| **Claude spec proposal** | 500k/h, 5M/day — **no economic derivation**, marked pending Matt | **LOW as evidence** |
| **Reddit R8** | "Threat model with defined scope and **budget**" — doctrine alignment | **LOW** — pattern only |
| **Actual per-iteration defender token counts** | **NOT MEASURED** — self-directed loop not wired to envelope yet | **GAP** |

**Honest gap:** We do not yet have production telemetry of tokens per Full Matrix iteration. Cap decision is **doctrine + headroom math + kill-switch independence**, not measured burn curves.

---

## 3. Headroom math (why 5M may choke Full Matrix)

Assumed future self-directed loop @ Matt's **15-min heartbeat** = **96 ticks/day**.

| Tokens per iteration | Daily spend if every tick runs | vs 5M cap | vs 8M cap |
|---------------------|--------------------------------|-----------|-----------|
| 25,000 | 2.4M | OK | OK |
| 50,000 | 4.8M | **Borderline** | OK |
| 75,000 | 7.2M | **SUSPEND false-positive** | OK |
| 100,000 | 9.6M | SUSPEND | **Borderline** |

Full Matrix (smash + mesh + iceberg + purple + integrity) on complex paths plausibly lands **50k–100k tokens/tick** once LLM-backed loops wire in.

**Derived:** 5M/day risks **healthy Full Matrix runs hitting SUSPENDED** before M4/Gate C soak. 8M/day adds ~60% headroom while T1 still hard-stops breach.

**Hourly cap 800k** maintains **1/10 of day cap** burst ratio (same structure as 500k/5M proposal) — day cap binds sustained ops; hour cap catches burst runaway into T1.

---

## 4. Risk trade (is 8M the smartest move?)

| Factor | 5M/day | 8M/day | Winner |
|--------|--------|--------|--------|
| False SUSPEND on legitimate Full Matrix | Higher risk | Lower risk | **8M** |
| Max damage if envelope fails entirely | ~$75/day equiv | ~$120/day equiv | 5M (slightly) |
| T1/T3 protection unchanged | Same | Same | **Tie** |
| M4 48h theoretical max burn | 10M tokens | 16M tokens | 5M (slightly) |
| AGI §6 non-goal (autonomy without cap) | Satisfied | Satisfied | **Tie** |
| Evidence-backed precision | Neither — both proposals | Neither — both proposals | **Tie until soak measures** |

**Verdict:** **8M tokens/day is the smarter move** given current evidence **if** the goal is Full Matrix + future 15-min soak without false-positive SUSPEND, **and** T1/T3 remain the real gatekeepers (they do — proven).

8M is **not** "unlimited headroom" — it is a **higher ceiling** on the same fail-closed governor. The envelope does not spend 8M; it **allows up to** 8M before SUSPEND.

**What would be smarter later (not instead of now):** Gate C 15-min soak records **actual tokens/tick** on Full Matrix stack → revise cap from measurement, not guess.

---

## 5. What 8M does NOT do

- Does not replace dead-man switch (T2/T3)
- Does not unblock M4 or claim PERFECT
- Does not convert AFE display into enforcement
- Does not remove need for human `ack_seq` every 30 min (ACK_STALE_MS = 2×15min)

---

## 6. Matt sign-off record

```text
Decision: DEFAULT_PER_DAY_CAP = 8_000_000 tokens
          DEFAULT_PER_HOUR_CAP = 800_000 tokens
Rationale: Full Matrix intelligence headroom; T1/T3 remain kill switch
Frozen in: chaos/mmi_control_envelope.py, architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md
Revisit trigger: Gate C soak produces measured tokens/tick variance > ±20% from assumptions above
```
