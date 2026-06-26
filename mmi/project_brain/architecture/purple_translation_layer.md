# Purple Translation Layer

Status: `RESEARCH_DESIGN`

Related targets: `#43 Geo-Context`, `#70 Final Review Agent`, future Blue/Purple
evidence modules.

## Purpose

The Purple Translation Layer turns defensive evidence into operator-ready
security intelligence. It is not a scanner and not an exploit system.

Primary loop:

```text
Blue evidence -> normalized facts -> Purple gap analysis -> detection/remediation draft -> human review
```

## Defensive-First Roadmap

### Phase 1: Blue Analysis Module

Goal: learn to see before learning to act.

Inputs:

- PCAP files from owned/lab environments
- JSON logs from SIEM, firewall, endpoint, or cloud controls
- screenshots of exposed portals or dashboards
- configuration files such as YAML, XML, or policy exports
- scanner output supplied by the operator, such as Nmap XML

Output:

- normalized observed facts
- confidence
- source provenance
- evidence references
- no remediation action by itself

### Phase 2: Purple Correlation Layer

Goal: compare observed facts against an ideal or signed baseline.

Examples:

- observed state: interface public
- expected state: interface behind VPN or Zero Trust
- gap: exposed management surface
- output: business risk summary plus admin remediation draft

The Purple layer can draft detection rules or remediation notes, but cannot
deploy them.

### Phase 3: Red/Safe Simulation

Goal: diagnostic probing only after Blue/Purple evidence handling is proven.

Rules:

- no autonomous exploitation
- no customer scanning without explicit authorization
- lab or owned environments only unless separately authorized
- high-sensitivity targets block probing by default
- Blue/Purple gate any diagnostic action

## Unified Fact Schema Draft

```json
{
  "fact_id": "fact_000001",
  "source_module": "blue_analysis_v1",
  "source_type": "pcap|json_log|screenshot|config|scanner_output|manual_note",
  "target_identifier": "host_or_asset_ref",
  "tenant_id": "tenant_or_lab_ref",
  "observation_type": "ServiceBanner",
  "content_summary": "Modbus/TCP service detected on port 502",
  "evidence_ref": "path_or_hash_or_record_id",
  "confidence_score": 0.98,
  "risk_impact": "high",
  "sensitivity": "low|medium|high|critical",
  "created_at": "2026-06-26T00:00:00Z"
}
```

Schema notes:

- `content_summary` must avoid raw secrets, credentials, tokens, or private
  customer data.
- `evidence_ref` points to evidence; it should not inline sensitive raw content.
- `risk_impact` is advisory until a signed rubric defines scoring.
- `sensitivity` controls whether later safe simulation is blocked.

## Boundary

- No build authority.
- No production dispatch.
- No active probing.
- No exploit generation.
- No deployment of generated rules.
- No AUTH-5.

## Next Design Step

Draft a dedicated Blue Analysis Module contract or design brief that defines:

- closed input types
- fact schema fields
- prohibited content
- evidence reference rules
- confidence vocabulary
- tenant isolation
- review and audit path

## Agentic Swarm Blue Team Command Center Addendum

Status: `RESEARCH_DESIGN`

This addendum captures the agentic Blue Team command-center concept as a
future architecture direction. It does not authorize autonomous response,
customer scanning, production mailbox actions, deception engagement, or build.

### Candidate Swarm Roles

- Orchestrator: receives an email alert or evidence packet, assigns bounded
  analysis tasks, aggregates findings, and emits an operator-facing decision
  packet.
- Forensic Agent: parses structural email evidence such as headers, SPF, DKIM,
  DMARC, hop path, attachment metadata, and sender infrastructure.
- Behavioral Context Agent: reviews language, urgency, authority pressure, and
  relationship-pattern evidence against approved enterprise context.
- Threat Intel Agent: enriches domains, registrars, indicators, and known
  reputation signals from approved feeds or operator-supplied data.
- Response Planner: drafts possible containment actions, but does not execute
  them without signed authority and human approval.
- Deception Research Module: parks honeypot/counter-engagement ideas behind
  legal and operator authorization. No autonomous replies to attackers.

### Safe Feature Classes

- Parallel read-only analysis of the same email/evidence packet.
- Agent disagreement summary with evidence references.
- Business-risk translation for BEC, invoice diversion, impersonation, and
  vendor-payment anomalies.
- ERP/accounting cross-check design for purchase order, invoice amount, and
  known bank-detail matching.
- Human-in-the-loop approval matrix for any mailbox, account, ERP, or external
  reporting action.
- Explainable evidence trail for analysts. Do not expose hidden chain-of-thought;
  provide concise rationale, evidence references, confidence, and rule hits.
- Threat repository update proposals that require review before merge or
  deployment.

### Parked / High-Liability Ideas

These ideas may be useful research, but they are not buildable until a separate
legal/safety contract exists:

- AI counter-scam or dynamic honeypot engagement with real attackers.
- Collecting mule bank accounts, wallets, or drop locations through autonomous
  interaction.
- Autonomous global clawback, account lockout, token revocation, or mailbox
  deletion.
- Polymorphic malware or payload modification.
- Automatic prompt mutation across production agents.
- Automatic deployment of generated YARA, Suricata, SIEM, mail-rule, or EDR
  rules.

### Guardrail Direction

- Read-only first.
- Draft-only response planning.
- Human approval for all destructive, customer-facing, external, or production
  actions.
- Tenant isolation on every fact, enrichment, and decision packet.
- Approved-tool registry before any external lookup.
- No hidden autonomous escalation from analysis to action.

### Candidate Project-Brain Structure

Future architecture files can be split when this branch becomes active:

```text
mmi/project_brain/architecture/agentic_swarm/
  swarm_hierarchy.md
  agent_role_boundaries.md
  tool_registry.md
  hitl_governance_matrix.md
  safety_guardrails.md
```

### Contract Direction

The first buildable contract should not be the full swarm. The safer first
contract is a Blue Analysis Module that accepts bounded evidence packets and
emits normalized facts plus an explainable analyst summary. Response,
deception, external lookup, and production action remain out of scope.
