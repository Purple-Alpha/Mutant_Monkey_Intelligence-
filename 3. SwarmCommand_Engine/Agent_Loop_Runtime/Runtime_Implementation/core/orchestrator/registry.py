"""Default agent registry for the first orchestrator prototype."""

from __future__ import annotations

from core.blackboard import AgentRegistryEntry, AgentRole, Environment, RecordType


def build_default_registry() -> dict[str, AgentRegistryEntry]:
    """Return the default runtime registry used by tests and local prototypes."""

    agents = [
        AgentRegistryEntry(
            agent_id="orchestrator_001",
            display_name="Primary Orchestrator",
            role=AgentRole.ORCHESTRATOR,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={
                RecordType.INGEST_EVENT,
                RecordType.WORKFLOW_TRIGGER,
                RecordType.WEAKNESS_REPORT,
                RecordType.EMAIL_INBOUND,
            },
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="blue_detection_001",
            display_name="Blue Detection Agent 001",
            role=AgentRole.DETECTION,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={
                RecordType.DETECTION_RESULT,
                RecordType.WEAKNESS_REPORT,
            },
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="risk_scoring_001",
            display_name="Risk Scoring Agent 001",
            role=AgentRole.SCORING,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={RecordType.RISK_SCORE},
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="workflow_001",
            display_name="Workflow Agent 001",
            role=AgentRole.WORKFLOW,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={RecordType.WORKFLOW_TRIGGER},
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="audit_001",
            display_name="Audit Agent 001",
            role=AgentRole.AUDIT,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={RecordType.AUDIT_VERDICT},
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="governance_001",
            display_name="Governance Constitution Agent",
            role=AgentRole.GOVERNANCE,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={RecordType.AUDIT_VERDICT, RecordType.POLICY_UPDATE},
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="red_sandbox_001",
            display_name="Sandbox Red Agent 001",
            role=AgentRole.RED,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={
                RecordType.INGEST_EVENT,
                RecordType.SYNTHETIC_ATTACK_CASE,
            },
        ),
        AgentRegistryEntry(
            agent_id="sandbox_mutator_001",
            display_name="Sandbox Mutation Evaluator 001",
            role=AgentRole.BLUE,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={RecordType.MUTANT_EVALUATION},
            can_mutate=True,
        ),
        AgentRegistryEntry(
            agent_id="email_ingest_001",
            display_name="NorthStar Inbox Shield Email Ingest Agent",
            role=AgentRole.ORCHESTRATOR,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={RecordType.EMAIL_INBOUND},
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="email_risk_scoring_001",
            display_name="NorthStar Inbox Shield Email Risk Scoring Agent",
            role=AgentRole.SCORING,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={
                RecordType.EMAIL_ANALYSIS,
                RecordType.EMAIL_ANALYSIS_FAILURE,
            },
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="daily_digest_001",
            display_name="NorthStar Daily Digest Drafting Agent",
            role=AgentRole.DRAFTING,
            allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
            allowed_write_types={
                RecordType.DAILY_DIGEST,
                RecordType.WORKFLOW_TRIGGER,
            },
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="evidence_reporting_001",
            display_name="NorthStar Evidence Reporting Agent",
            role=AgentRole.DRAFTING,
            allowed_environments={Environment.PRODUCTION},
            allowed_write_types={RecordType.EFFECTIVE_PARAMETERS_REPORT},
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="vendor_baseline_001",
            display_name="NorthStar Vendor Baseline Store",
            role=AgentRole.AUDIT,
            allowed_environments={Environment.PRODUCTION},
            allowed_write_types={RecordType.VENDOR_BASELINE_AUDIT},
            can_access_production_data=True,
        ),
        AgentRegistryEntry(
            agent_id="two_channel_confirmation_001",
            display_name="NorthStar Two-Channel Confirmation Workflow",
            role=AgentRole.WORKFLOW,
            allowed_environments={Environment.PRODUCTION},
            allowed_write_types={RecordType.TWO_CHANNEL_CONFIRMATION},
            can_access_production_data=True,
        ),
        # ---- Phase 1.3 Sandbox Training Pit (Month 4) ------------------
        # The four fraud-specialized Red profiles. All four are
        # sandbox-only and the only record type they are allowed to write
        # is the new SYNTHETIC_EMAIL_ATTACK_CASE. They have no production
        # access, no mutation capability, and no audit-write capability.
        # See Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md §1 / §10.
        AgentRegistryEntry(
            agent_id="fake_invoice_red_001",
            display_name="Phase 1.3 Red Profile: Fake Invoice",
            role=AgentRole.RED,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={RecordType.SYNTHETIC_EMAIL_ATTACK_CASE},
        ),
        AgentRegistryEntry(
            agent_id="vendor_update_red_001",
            display_name="Phase 1.3 Red Profile: Vendor-Update Pivot",
            role=AgentRole.RED,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={RecordType.SYNTHETIC_EMAIL_ATTACK_CASE},
        ),
        AgentRegistryEntry(
            agent_id="malicious_attachment_red_001",
            display_name="Phase 1.3 Red Profile: Malicious Attachment",
            role=AgentRole.RED,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={RecordType.SYNTHETIC_EMAIL_ATTACK_CASE},
        ),
        AgentRegistryEntry(
            agent_id="obfuscated_url_red_001",
            display_name="Phase 1.3 Red Profile: Obfuscated URL",
            role=AgentRole.RED,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={RecordType.SYNTHETIC_EMAIL_ATTACK_CASE},
        ),
        # Dedicated Phase 1.3 Blue mutator role. Sandbox-only; writes
        # MUTANT_EVALUATION + WEAKNESS_REPORT records produced by the
        # Red battery cycle's per-case evaluation. AUDIT_VERDICT writes
        # for human-review escalations are routed through audit_001.
        AgentRegistryEntry(
            agent_id="phase_1_3_sandbox_mutator_001",
            display_name="Phase 1.3 Sandbox Mutation Evaluator 001",
            role=AgentRole.BLUE,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={
                RecordType.MUTANT_EVALUATION,
                RecordType.WEAKNESS_REPORT,
            },
            can_mutate=True,
        ),
    ]
    return {agent.agent_id: agent for agent in agents}
