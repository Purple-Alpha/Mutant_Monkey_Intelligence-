# Network Mutator

**Status:** `RESEARCH_DESIGN` | **Component:** Swarm Command Reality Controller  
**Objective:** Ephemeral topology and moving target defense (MTD).

> **Authority:** Research doctrine only. Not build authorization. See `README.md`.

---

## 1. Mission Statement

The `network-mutator` is the entropy engine of Swarm Command. Its mandate is to
negate the value of an attacker's network reconnaissance. By continuously rotating
internal IP addresses, service roles, and hostnames, it renders any "map" an attacker
builds obsolete within minutes, forcing them to restart their scan — and exposing
their TTPs in the process.

---

## 2. Operational Tactics

- **Ephemeral Addressing:** Dynamically reassigns internal IP addresses for decoy
  services via software-defined networking (SDN) controllers.
- **Service Ghosting:** Instantiates and kills "ghost" services on open ports.
- **Topological Shifting:** Updates the "breadcrumbs" planted by the
  `beacon-injector`. If a decoy document points to a server at `10.0.0.5`, the
  mutator ensures that as the document is moved, the network backend shifts roles
  to maintain the "deception narrative."

---

## 3. Intelligence Outputs (The Data Stream)

When the mutator shifts, it logs the "Delta" to the MMI project brain:

- **Recon-Correlation:** Maps the exact moment an attacker's scan triggers an infrastructure shift.
- **Scan-Pattern Attribution:** Records the speed and depth of port scanning activity.
- **Lateral Movement Trap-Detection:** Alerts the Swarm if an attacker attempts to "follow" a shifted service.

---

## 4. Stealth and Integrity Protocols

- **Synchronization:** Must stay synced with `geo-fence-manager` so regional persona stays consistent.
- **Non-Disruptive Mutation:** Shifts at the control-plane level; infrastructure remains "open" from the attacker's perspective.
- **Attacker-Triggered Rotation:** "Aggressive Mode" mutates only when the attacker probes a specific asset.

---

## 5. Integration Architecture

- **Input:** Real-time telemetry from the `reality-controller` regarding scan intensity.
- **Process:** `network-mutator` calculates the next "Topology State" and updates virtual switch and DNS/DHCP configurations.
- **Output:** A `State-Change-Log` pushed to MMI project brain to update the global world model of the decoy environment.
