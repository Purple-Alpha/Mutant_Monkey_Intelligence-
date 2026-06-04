# NorthStar + SwarmCommand

**Operating domain:** `mutantmonkeysecurity.com` (Mutant Monkey Security; registered by the operator 2026-06-04, confirmed via WHOIS).

Working name is in transition. Rename-candidate history and screening criteria live in `PROJECT_ACTIVITY_LOG.md`. The canonical product thesis is `VISION.md`.

## What this is

A self-evolving multi-agent cybersecurity defense system, sold through MSPs to SMBs.

- **Stage A (now):** analyze email, score fraud/ransomware-precursor threats, and produce an auditable evidence package with full provenance. Analyze-and-recommend only — no autonomous action.
- **Stage B / C (later):** bounded autonomous defense and a continuous-learning defense swarm.

See `VISION.md` for the full Stage A -> B -> C arc and the seven non-negotiables (kill switch always wins, full audit, reversibility, tenant isolation, signed promotion, human review of adversarial updates, operator approval for client-facing actions).

## Start here

- `AGENTS.md` - operating doctrine; read every session. Includes the canonical build loop (§3.2).
- `VISION.md` - product thesis + the seven non-negotiables.
- `PROJECT_HANDSHAKE.md` - current build target, verification baseline, and resume point.
- `MASTER_INDEX.md` - canonical list of every project artifact.
- `LINUX_WORKFLOW_QUICKSTART.md` - operator terminal basics.

## Development surface

WSL2 Ubuntu at `/home/socialarchitect/northstar`. The runtime + tests live under
`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`.
