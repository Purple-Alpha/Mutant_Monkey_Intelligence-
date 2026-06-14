"""Closed Cortex / Immune Interface vocabulary.

Governing contract
------------------
``4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol). Scoreboard row #96 (Layer 6 Control Plane).

The interface is not a new organ, service, message bus, or authority. These
closed enums define only the legal boundary vocabulary and the forbidden
hidden-channel classes from the signed contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Organ(str, Enum):
    CORTEX = "cortex"
    IMMUNE = "immune"


class CortexComponent(str, Enum):
    KNOWLEDGE_AGENT = "knowledge_agent"
    DETECTION_AGENT = "detection_agent"
    CORTEX_PROCESS = "cortex_process"


class ImmuneComponent(str, Enum):
    MODE_CONTROLLER = "mode_controller"
    PRIVACY_FILTER = "privacy_filter"
    BLAST_RADIUS_CONTROLLER = "blast_radius_controller"
    WATCHER_AGENT = "watcher_agent"
    FISSION = "fission"
    MUTATION_ENGINE = "mutation_engine"
    RECONCILIATION_AGENT = "reconciliation_agent"
    SAFE_STOP_STATE_MACHINE = "safe_stop_state_machine"
    COLLECTIVE_IMMUNE_SYSTEM = "collective_immune_system"
    GOVERNED_INGESTION_PIPELINE = "governed_ingestion_pipeline"


class HandoffPoint(str, Enum):
    EVIDENCE_LEDGER = "evidence_ledger"
    OBSERVATION_LOG = "observation_log"
    VERDICT_LEDGER = "verdict_ledger"
    TENANT_BASELINE_STORE = "tenant_baseline_store"
    ALL_COMPONENTS = "all_components"
    CORTEX_COMPONENT = "cortex_component"
    IMMUNE_COMPONENT = "immune_component"


class CortexToImmuneSignal(str, Enum):
    EVIDENCE_RECORD = "evidence_record"
    OBSERVATION_RECORD = "observation_record"
    ANOMALY_SIGNAL = "anomaly_signal"
    HYPOTHESIS_RECORD = "hypothesis_record"


class ImmuneToCortexSignal(str, Enum):
    MODE_STATE_BROADCAST = "mode_state_broadcast"
    RECONCILIATION_OUTPUT = "reconciliation_output"
    SAFE_STOP_STATE = "safe_stop_state"
    GOVERNED_BASELINE_UPDATE = "governed_baseline_update"


class BaselineValidationGate(str, Enum):
    SCHEMA = "schema_validation"
    PROVENANCE = "provenance_validation"
    TENANT_SCOPE = "tenant_scope_validation"
    RECONCILIATION_CLOSURE = "reconciliation_closure_confirmation"
    AUDIT_LOG = "audit_log_write"
    ROLLBACK_EVIDENCE = "rollback_evidence_creation"


class HiddenChannelType(str, Enum):
    SHARED_MUTABLE_STATE = "shared_mutable_state"
    DIRECT_FUNCTION_CALL = "direct_function_call"
    LOG_SIDE_CHANNEL = "log_side_channel"
    IMPLICIT_CONFIG_SHARING = "implicit_config_sharing"


class InterfaceDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    VIOLATION = "violation"


@dataclass(frozen=True)
class LegalCortexSignalRule:
    signal: CortexToImmuneSignal
    source: CortexComponent
    target: HandoffPoint
    condition: str


@dataclass(frozen=True)
class LegalImmuneSignalRule:
    signal: ImmuneToCortexSignal
    source: ImmuneComponent
    target: HandoffPoint
    condition: str


LEGAL_CORTEX_TO_IMMUNE: frozenset[LegalCortexSignalRule] = frozenset(
    {
        LegalCortexSignalRule(
            CortexToImmuneSignal.EVIDENCE_RECORD,
            CortexComponent.DETECTION_AGENT,
            HandoffPoint.EVIDENCE_LEDGER,
            "after local analysis complete",
        ),
        LegalCortexSignalRule(
            CortexToImmuneSignal.OBSERVATION_RECORD,
            CortexComponent.DETECTION_AGENT,
            HandoffPoint.OBSERVATION_LOG,
            "after signal classified",
        ),
        LegalCortexSignalRule(
            CortexToImmuneSignal.ANOMALY_SIGNAL,
            CortexComponent.DETECTION_AGENT,
            HandoffPoint.OBSERVATION_LOG,
            "when local threshold exceeded",
        ),
        LegalCortexSignalRule(
            CortexToImmuneSignal.HYPOTHESIS_RECORD,
            CortexComponent.CORTEX_PROCESS,
            HandoffPoint.EVIDENCE_LEDGER,
            "when hypothesis formed",
        ),
    }
)


LEGAL_IMMUNE_TO_CORTEX: frozenset[LegalImmuneSignalRule] = frozenset(
    {
        LegalImmuneSignalRule(
            ImmuneToCortexSignal.MODE_STATE_BROADCAST,
            ImmuneComponent.MODE_CONTROLLER,
            HandoffPoint.ALL_COMPONENTS,
            "on mode transition",
        ),
        LegalImmuneSignalRule(
            ImmuneToCortexSignal.RECONCILIATION_OUTPUT,
            ImmuneComponent.RECONCILIATION_AGENT,
            HandoffPoint.EVIDENCE_LEDGER,
            "on verdict produced",
        ),
        LegalImmuneSignalRule(
            ImmuneToCortexSignal.SAFE_STOP_STATE,
            ImmuneComponent.SAFE_STOP_STATE_MACHINE,
            HandoffPoint.ALL_COMPONENTS,
            "on safe-stop entry or exit",
        ),
        LegalImmuneSignalRule(
            ImmuneToCortexSignal.GOVERNED_BASELINE_UPDATE,
            ImmuneComponent.GOVERNED_INGESTION_PIPELINE,
            HandoffPoint.TENANT_BASELINE_STORE,
            "after full ingestion validation passes",
        ),
    }
)


__all__ = [
    "Organ",
    "CortexComponent",
    "ImmuneComponent",
    "HandoffPoint",
    "CortexToImmuneSignal",
    "ImmuneToCortexSignal",
    "BaselineValidationGate",
    "HiddenChannelType",
    "InterfaceDecision",
    "LegalCortexSignalRule",
    "LegalImmuneSignalRule",
    "LEGAL_CORTEX_TO_IMMUNE",
    "LEGAL_IMMUNE_TO_CORTEX",
]
