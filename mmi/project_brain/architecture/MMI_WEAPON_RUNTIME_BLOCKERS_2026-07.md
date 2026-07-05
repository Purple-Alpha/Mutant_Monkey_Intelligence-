# MMI Weapon Runtime Blockers — 2026-07

**Status:** ARCHITECTURE ANALYSIS — NOT BUILD AUTH  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-01  
**Purpose:** Concrete bottlenecks blocking Track A weapon deployment against Track B runtime — and required bypass patterns.

**Related:**

* `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md`
* `architecture/MMI_CONCEPT_INVENTORY_AND_GAPS_2026-07.md`
* `chaos/MMI_SWARM_BLUEPRINT_LUNG_V1_2026-06.md`
* `lanes/RESEARCH_LUNG_V2_REFACTOR_2026-06.md`

---

## Context

Track A (weapon) and Track B (built ops runtime) laid side-by-side expose where the system will seize up.

This is not an LLM logic or prompt phrasing issue. It is a fundamental collision between the software runtime actually built (Track B) and the low-level OS/infrastructure capabilities the weapon requires (Track A).

If Lung v1/v2 or the 70→700 fork storm is coded inside a standard high-level Python application layer, it will fail to deploy.

---

## 1. The Kernel-Space vs. User-Space Blindspot (The V2 Refactor Wall)

Lung v2 lists WFP (Windows Filtering Platform), WDAC (Windows Defender Application Control), and OS-level ACLs.

**The Issue:** Python cannot natively control or hot-swap kernel-level WFP callout drivers or update WDAC application policies on the fly while under an active exploit injection. If an agent is compromised in user-space, it cannot tell the host OS to change its own firewall rules without possessing local Administrator/SYSTEM privileges—which violates the rule against giving corrupt agents real permissions.

**The Fix:** You cannot write the Lung as a pure Python script. It must be split into a **User-Space Agent Mesh** and a **detached, immutable Host-Space Daemon** (written in Go or Rust) running as a system service. The Python agents only communicate with this daemon via a local, highly restricted Unix socket or named pipe. When a critic flags an anomaly, it tells the daemon, and the daemon violently severs the network interface or isolates the process using native OS container APIs (like Linux cgroups or Windows Job Objects).

---

## 2. The Multi-Model Memory Asynchrony Block

The concept relies on Polyglot Lane Routing and Heterogeneous Defensive Inflation across different model backends (OpenAI, Gemini, Claude).

**The Issue:** Different frontier models have wildly different API latencies, token processing speeds, and state tracking structures. If you trigger an elastic inflation of 700 agents across 3 different commercial providers simultaneously during an attack, you will hit aggressive API Rate Limits (TPM/RPM limits) within seconds. The attacker can intentionally weaponize your inflation against you, triggering a self-induced Denial of Service (DoS) where your provider accounts get locked down.

**The Fix:** The inflation must rely heavily on **local, lightweight, open-source model shards** (like 8B LLaMA or Mistral instances) deployed in pre-warmed, ephemeral local containers (Docker/Podman). Commercial APIs should only be used for the air-gapped, high-intelligence Core/Validator layers.

---

## 3. The Doctrine Code Mutex (The Orchestrator Conflict)

The inventory doc highlights a fatal architectural conflict: `MMI_ORCHESTRATOR_SCOPE.md` strictly dictates no auto-spawned bots, yet the weapon demands elastic inflation.

**The Issue:** If orchestrator code is written to prevent dynamic process creation to maintain a clean environment, any script that attempts to fork a new agent node will trigger internal P1–P8 guardrails. The system will fight itself, flagging its own defensive inflation as an active internal threat.

**The Fix:** Formalize **"The Air-Lock Pattern"**. The orchestrator loop never spawns an agent. Instead, a fixed pool of 700 micro-containers is created at system boot in a dormant, stateless **Sleep** mode. Inflation doesn't mean creating new code; it means the orchestrator dynamically **wakes up** pre-existing, air-gapped container runtimes and streams the active context to them via the signed JSON/nonce layer.

---

## 4. The Token Leakage in Evidence Harvesting

The Evidence Harvesting Hub is meant to read malicious payload logs to generate draft system prompt patches.

**The Issue:** If a hacker executes an advanced data-extraction or prompt-injection attack, the malicious payload itself is wrapped in the logs. If the harvesting agent reads those logs uncritically to draft a patch, it can be cross-contaminated by the log data. The act of analyzing the attack vector can trick the patch-generation model into embedding an exploit or a back-door directly into the new draft prompt.

**The Fix:** Pass harvested logs through a **completely deterministic string sanitizer and token-tokenizer** before any LLM reads it. It must strip out all formatting, escape characters, markdown blocks, and execution syntax, reducing the attack string to raw, inert hex characters or delimited strings that cannot execute semantically.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Matt runtime blocker analysis filed verbatim |
