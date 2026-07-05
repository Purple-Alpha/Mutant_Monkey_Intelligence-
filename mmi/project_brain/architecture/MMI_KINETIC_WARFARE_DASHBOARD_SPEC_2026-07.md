# MMI Kinetic Warfare & Approval Console — Dashboard Spec

**Status:** PARTIAL — slot map + AFE ledger + WebSocket live (2026-06-28)  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-01  

**Purpose:** Not a passive data-visualization tool. A **Kinetic Warfare & Approval Console** for the defensive weapon stack.

The dashboard is three-fold:

1. **Human-in-the-Loop Air-Lock:** Review and sign off on draft system patches from the Evidence Harvesting Hub before production deploy.
2. **Track Attacker Financial Bleeding:** Monitor computational API credit and time the Tarpit forces the adversary to waste.
3. **Weapon Control Panel:** Manually sever compromised nodes, flush container caches, or trigger full swarm defensive inflation if automated threshold needs override.

**Related:** `chaos/war_room_dashboard_api.py` (concept API layer); `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` §19, §22.

---

## Dashboard Core UI Specifications (The Command Center)

The dashboard is divided into three high-utility operational quadrants:

### 1. The Patch Staging Area (The Immune Gate)

* **The View:** A side-by-side git-diff display. On the left: the current system prompt. On the right: the newly sanitized, auto-generated draft patch compiled from the attacker's neutralized payload signatures.
* **The Action:** A prominent **[EXECUTE IMMUNIZATION]** button requiring an asymmetric cryptographic signature (e.g., your private Ed25519 key) to merge the patch into the production main branch.

### 2. The Asymmetric Economics Ledger (The Retaliation Counter)

* **The View:** A financial ledger displaying two contrasting numbers:
  * **Our Cost:** Local shard compute cost (fractions of a cent for running local 8B models in sleep containers).
  * **Their Cost:** Estimated adversary token spend based on common API pricing (OpenAI/Anthropic commercial rates) for processing the massive, looping, recursive junk data fed to them by your Tarpit.
* **The Metric:** A live multiplier display showing your Asymmetric Return on Investment (e.g., **"1:420 – Attacker spending $420 for every $1 we spend on containment"**).

### 3. The Swarm Arena Telemetry Map

* **The View:** A clean matrix visualization of your active container slots (Index 001–700).
  * **Green Slots:** Active, trusted core workers.
  * **Grey Slots:** Dormant, pre-warmed Air-Lock containers waiting in `SLEEP` mode.
  * **Red Slots:** Containers that have been compromised, stripped of permissions, and seamlessly hot-routed to the MirrorDimensionRouter.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Kinetic warfare dashboard spec filed verbatim |
| 1.1 | 2026-06-28 | FastAPI console: `scripts/kinetic_war_room_server.py`, `chaos/kinetic_telemetry.py` |

---

## Run (chaos lab local)

```bash
python3 -m venv .venv_kinetic
.venv_kinetic/bin/pip install -r requirements_kinetic_console.txt
.venv_kinetic/bin/python3 scripts/kinetic_war_room_server.py --lab-id m2_001
# Open http://127.0.0.1:8765/ — WebSocket /ws/live pushes every 2s
# REST: GET /api/slots, /api/afe, /api/telemetry
```

**Built:** Swarm slot map (001–700 green/grey/red), AFE ledger, patch staging preview from mirror cells.  
**Not built:** Ed25519 [EXECUTE IMMUNIZATION], manual sever/flush/inflate controls.
