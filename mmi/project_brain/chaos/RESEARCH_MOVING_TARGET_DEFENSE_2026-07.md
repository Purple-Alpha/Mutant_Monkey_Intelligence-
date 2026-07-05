# MTD Research Lane: Shifting the Adversarial Attack Surface

**Status:** RESEARCH — NOT BUILT  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-01  
**Path:** `mmi/project_brain/chaos/RESEARCH_MOVING_TARGET_DEFENSE_2026-07.md`

This research lane covers the core mechanics of Moving Target Defense (MTD) as applied to agentic swarms. Standard security models treat systems as static targets. MTD shifts the defensive paradigm. It introduces continuous, controlled changes across the agent runtime environment. This drastically increases the cost, time, and complexity for an attacker trying to exploit the swarm.

By running this protocol, you break the stability an attacker requires to maintain persistence or execute multi-stage prompt injections.

**Related:** `architecture/MMI_ORCHESTRATOR_SCOPE.md` Addendum 04 (Air-Lock); `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` §9, §14.

---

## 1. Core Philosophy of Agent-Level MTD

Traditional software security patches vulnerabilities to keep a system static and secure. Mutant Monkey Intelligence (MMI) assumes patches will fail, zero-days will occur, and agents *will* be compromised.

Moving Target Defense (MTD) handles this by constantly altering the system's structural and operational characteristics over time. The goal is to minimize the lifetime validity of any exploit payload. If an attacker maps the swarm's layout at $T_0$, that map must be completely obsolete and useless by $T_1$.

---

## 2. Dimension Shifting Matrix

To execute MTD without degrading the core semantic reasoning of the models, the system moves targets across three distinct execution layers:

### A. Network-Edge Nonce Chaining

* **The Mechanism:** Eliminate static API routes or predictable local Inter-Process Communication (IPC) pipes.
* **The MTD Shift:** Every agent-to-agent communication endpoint relies on a dynamic, cryptographically generated token space. Message routing targets are bound to a rolling HMAC-SHA256 signature chain synced with a secure core hardware clock.
* **Adversarial Cost:** An attacker cannot intercept a message package, alter the payload, and re-inject it into the stream. By the time the modified packet hits the mesh, the validation window has expired, and the expected routing nonce has shifted.

### B. Context & Prompt Sharding (Semantic MTD)

* **The Mechanism:** Standard agents use long, monolithic system prompts that hold all system capabilities. This makes them highly vulnerable to context-leaking attacks.
* **The MTD Shift:** Split the agent's core identity and capabilities into stateless, micro-prompt shards.
* **The Realization:** When a task is routed to an Air-Lock container, the orchestrator dynamically randomizes the layout order of safety boundaries, utility instructions, and structural XML tags inside the prompt.
* **Adversarial Cost:** Automated prompt-injection scripts look for exact phrasing delimiters (e.g., `#### System Instructions`). Randomly shuffling structural syntax breaks the rigid spatial layouts that exploit payloads rely on to hijack model attention weights.

### C. Backend Engine Shuffling (Polyglot Rotation)

* **The Mechanism:** Avoid pinning an active agent track to a single model architecture or deployment stack.
* **The MTD Shift:** Route sequentially incoming steps of a single distributed task across completely different LLM families (e.g., Turn 1: Local LLaMA 8B $\rightarrow$ Turn 2: Claude Sonnet $\rightarrow$ Turn 3: Local Mistral).
* **Adversarial Cost:** Prompt engineering attacks are highly model-specific. An exploit written to trick a specific quantization of a LLaMA model will crash, error out, or get flagged when processed by the completely different neural weights of an Anthropic or Gemini engine.

---

## 3. Failure Modes & Remediation

Altering execution states on the fly introduces major engineering challenges. Below are the deterministic safety rules required to prevent self-induced system chaos:

| Failure Mode | Root Cause | MTD Mitigation Control |
| :--- | :--- | :--- |
| **State Desynchronization** | Network latency delays a packet past its cryptographic nonce validity window. | Enforce a strict $T_{\pm 1}$ sliding validation window. Accept the immediate past nonce slice to absorb transit jitter, then force termination if drift exceeds threshold. |
| **Context Drifting** | Randomizing prompt formatting alters the model's semantic output consistency. | Every randomized prompt permutation must pass through an ultra-fast, local automated schema evaluator block before deployment to ensure instructions match invariant system criteria. |
| **Cascading Token Starvation** | Rotating models across multiple providers trips unexpected external API rate caps or local container cold starts. | Bind MTD rotation strictly to a pre-warmed, local container cluster pool using the Air-Lock Pattern. Limit commercial cloud fallback routes to high-tier validator nodes only. |

---

## 4. Operational Metrics: Evaluating the Asymmetric Cost

To prove the MTD protocol is working, the Evidence Harvesting Hub tracks the following attack metrics inside the chaos lab:

* **Exploit Lifetime Duration (ELD):** Tracks the elapsed time between an active injection event and the automatic invalidation of that exploit vector via a system shift.
* **Attacker Financial Exhaustion (AFE):** Calculates the estimated API and infrastructure cost incurred by the adversary as they are forced to regenerate exploit iterations against a mutating schema.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | MTD research lane filed verbatim |
