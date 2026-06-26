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

