# Tarpit Orchestrator

**Status:** `RESEARCH_DESIGN` | **Component:** Swarm Command Reality Controller  
**Objective:** Attacker resource exhaustion and session prolongation.

> **Authority:** Research doctrine only. Not build authorization. See `README.md`.

---

## 1. Mission Statement

The `tarpit-orchestrator` is designed for **lab decoy environments** against
automated exploit-chains. Its mandate is to artificially inflate the "cost of
attack" by forcing the attacker's tools into permanent latency, partial-completion,
or recursive redirection — without ever dropping the connection in a way that
reveals active countermeasures.

---

## 2. Operational Tactics

- **Recursive Latency Injection:** Introduces calculated jitter and delay (e.g.,
  200ms to 5000ms), causing common attack tools to time out, retry, or behave
  sporadically.
- **Partial-Response Trapping:** Serves "broken" or "incomplete" responses —
  e.g., 200 OK header but payload at 1 byte per second.
- **Looping Decoys:** Redirects automated lateral movement through a "circular maze"
  of decoy services.

---

## 3. Intelligence Outputs (The Data Stream)

When an attacker is "tarpitted," the orchestrator streams forensic data to MMI project brain:

- **Tool-Chain Fingerprint:** Retry-logic and timeout behavior of the attacker's software.
- **Persistence Duration:** How long an attacker stays on a "slow" target before giving up.
- **Resource Cost-Calculation:** Estimated compute/time cost sunk into the decoy.

---

## 4. Stealth and Integrity Protocols

- **Adaptive Throttling:** Scaled by attacker behavior — cautious vs aggressive scanner.
- **Non-Refusal:** Never return 403 or connection reset; trap feels "available but burdened."
- **Ghost-Protocol:** Can mimic TCP-half-open states to tie up attacker thread limits.

---

## 5. Integration Architecture

- **Input:** Trigger signals from `network-mutator` (active scan) or `geo-fence-manager` (suspicious origin).
- **Process:** Configures edge-firewall/proxy rules for delay/looping logic.
- **Output:** Updates `Attacker-Session-Context` in MMI project brain so other modules treat this attacker as a "captured asset" for logging only — not autonomous action.
