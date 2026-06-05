# Consequence Matrix — Private Test-Data Store Q3 (Mesh / Network Reachability)

**Status:** Operator-triggered analysis (pre-§11, non-binding). Run 2026-06-04 per `Consequence_Matrix_Process.md`.
**This file surfaces second-order effects. Matt decides; the outcome is recorded in §Outcome.**

## Decision
**Decision:** Which private-network overlay reaches the self-hosted test-data store (MinIO) — managed mesh (Tailscale) vs self-hosted WireGuard — for `Private_Test_Data_Store_Deep_Dive.md` Q3 / D3.
**Date:** 2026-06-04
**Owner:** Matt Nichol
**Why this matters:** The whole point of this store is data sovereignty — operator owns the keys, host, and network path (D1). The mesh choice decides *who you trust to coordinate reachability*. It is path-setting because it touches architecture, future autonomy, and (if the store ever moves toward production per Q7) legal/sovereignty posture. The spec itself (§10 Q3, failure mode 5 "sovereignty theater") flags this as Consequence-Matrix-worthy.

## Options
- **Option A — Tailscale (managed control plane):** A hosted coordination server handles key exchange / NAT traversal. Nodes connect over WireGuard under the hood, but the control plane is Tailscale-operated. Fast to stand up (minutes-to-hours), MagicDNS, ACLs, easy device add/remove.
- **Option B — Self-hosted WireGuard (full sovereignty):** You run the WireGuard config yourself — key generation, peer config, endpoint/port, NAT traversal. No third-party control plane. More setup and ongoing config management; full ownership of every trust boundary.
- **Option C — Headscale (self-hosted Tailscale control plane):** Open-source re-implementation of the Tailscale control server, self-hosted. Tailscale client UX + ACLs/MagicDNS, but you own the coordination server. Middle path: more setup than A, less raw-config toil than B.

## Short-Term Consequences (0-30 days)

| Option | Opens | Closes | Build Surface Added | Reduces Risk | Creates Risk | Pipeline Signal |
|---|---|---|---|---|---|---|
| A | Store reachable across your devices in hours; MagicDNS/ACLs out of the box | Nothing hard | Tailscale account + ACL config; one external dependency | Public-exposure risk (D3) handled cleanly — no port-forward needed | A third-party control plane coordinates connections (does not see artifact bytes, but sees device/connection metadata) | Fastest path to a working store; unblocks B-milestone follow-ons |
| B | Full-sovereignty path from day one | Easy multi-device onboarding; quick ACL changes | WireGuard keygen + per-peer config + endpoint/NAT handling, by hand | No third-party in the path at all | Setup/config error risk (a hand-rolled config is the likeliest *public-exposure* failure mode, ironically) | Slower to stand up; delays store availability |
| C | Tailscale-like UX with self-owned control plane | Little | Headscale server to deploy + maintain (+ its own durability) | No external control plane; still gets ACLs/MagicDNS | You now operate (and must keep up) a coordination server | Medium speed; more moving parts to babysit |

## Long-Term Consequences (3-12 months)

| Option | Architecture Lock-In | Trust / Credibility | Legal / Insurance Exposure | Maintenance Burden | Evidence / Data Value | Doctrine Drift Risk | Claim / Forbidden-Language Risk | Operator-Time Burden | Long-Term Reversibility |
|---|---|---|---|---|---|---|---|---|---|
| A | Mild — Tailscale identity/ACL model; client is standard WireGuard so exit is not hard | Fine for synthetic/lab data; a "we depend on Tailscale" footnote if a buyer ever audits sovereignty | Low *while synthetic-only* (D5); would need re-examination before any Q7 production use (connection metadata sits with a third party) | Low — Tailscale operates the hard part | Neutral | Low-to-mild — a third-party control plane slightly dents the "operator owns the network path" claim (sovereignty theater watch) | None | Low | **High** — client is WireGuard; migrating to B/C later is a config swap, not a data move |
| B | Toward fully self-owned networking | Strongest sovereignty story; nothing to footnote | Lowest — no third party in the path | **Higher** — you own keys, rotation, NAT, every peer | Neutral | Lowest — fully consistent with VISION local-first + D1 | None | **Higher** — ongoing config ownership | High — it's already the most self-owned end state |
| C | Toward self-owned Tailscale-compatible stack | Strong — self-owned control plane, good UX | Low — control plane is yours | Medium-high — you run + back up Headscale | Neutral | Low | None | Medium | High — Tailscale-client compatible |

## Decision Notes
- **Biggest upside (A):** working sovereign-enough store in hours, and because the client is plain WireGuard, choosing A now does **not** lock you out of B or C later — migration is a network-config change, not a data migration.
- **Biggest downside (A):** a third-party coordination/control plane sees connection + device metadata (not artifact contents). For synthetic data that is a footnote; for any future production/real-customer use (Q7) it becomes a real sovereignty question.
- **Hidden dependency:** Q7 (production boundary). If this store stays strictly test/lab forever — which is the recommended Q7 lock — A's third-party control plane is a low-stakes convenience. The moment Q7 is ever reopened toward real customer data, the mesh choice must be re-examined.
- **Assumption that must be true (A):** Tailscale's control plane never handling artifact bytes is acceptable, and connection metadata exposure is acceptable for synthetic data. (True today.)
- **Optionality killed:** essentially none by A (WireGuard client = portable). B kills the fast-onboarding convenience. C adds a server you must keep alive.
- **What A implicitly authorizes:** a standing dependency on a third-party network control plane for the lab environment.
- **Reverse trigger:** migrate A -> C/B if (a) Q7 is ever reopened toward real customer data, (b) Tailscale pricing/terms change, or (c) a buyer sovereignty audit requires zero third-party path.
- **Evidence needed before committing:** none beyond this matrix for synthetic-only v1; a fresh pass is required before any Q7 production reopen.
- Cell quality: all cells `estimate` except "Tailscale client is standard WireGuard" and "D5 synthetic-only" which are `fact`.

## Outcome
**Operator decision:** **Option B — self-hosted WireGuard.** Authorized by Matt Nichol 2026-06-05. Promoted to spec decision D15. (The operator initially leaned A/Tailscale on 2026-06-04, then overrode to B: he prefers the safest, fully-sovereign, self-hosted path — own sandbox, own keys, no third-party control plane — and explicitly accepts the steeper learning curve in order to "learn how to do this correctly first" rather than adopt a managed mesh and migrate later.)
**Reason:** B is the purest data-sovereignty end state: no third-party coordination/control plane sees even connection metadata, fully consistent with VISION local-first and D1 (operator owns keys/host/network path). The tradeoff is higher setup + ongoing config-ownership burden (keygen, per-peer config, endpoint/NAT) and the watch-item that a hand-rolled config is the likeliest public-exposure failure mode — mitigated by D3 (no public ingress) plus an external reachability check before the store holds anything. Operator explicitly accepts the learning curve. (Option C / Headscale remains the documented fallback if raw WireGuard config-management proves operationally too heavy — it keeps a self-owned control plane while easing multi-peer onboarding.)
**Review trigger or date:** Revisit only if WireGuard config-management proves operationally unsustainable (then consider Headscale/Option C) or if a future need changes the topology. No third-party-mesh review trigger applies — B already has no third party in the path.
