"""Layer 0 — Knowledge Foundation (Phase 2).

Governing contract
------------------
``4. Product_Roadmap/Phase2_Knowledge_Foundation_Agent_Design_Contract.md`` —
§11 SIGNED 2026-06-10 (Matt Nichol). Depends on Phase 1 Infrastructure (fe355da).

Six Layer 0 threat-intelligence agents. They **brief** the detection swarm; they
do not detect, score, flag, or produce verdicts, and they never write to
``core/blackboard/`` (P2-D1, P2-D7). Every briefing object is immutable so a
calling Layer 1 agent cannot modify it. Knowledge is static at build, seeded from
public threat-intelligence frameworks (P2-D4); no autonomous updates — mutation is
Phase 5 (P2-D5).

This package deliberately does **not** import ``core.blackboard``; that boundary
is enforced structurally and verified by each agent's adversarial test class.
"""

from .ai_gen_content_intel_agent import (
    AIGenContentBriefing,
    AIGenContentIntelAgent,
    ImageRatioThresholds,
)
from .bec_intel_agent import BECBriefing, BECIntelAgent
from .geo_intel_agent import GeoBriefing, GeoIntelAgent, TimeAnomalyWindow
from .phish_intel_agent import PhishBriefing, PhishIntelAgent
from .ransomware_intel_agent import RansomwareBriefing, RansomwareIntelAgent
from .trojan_delivery_intel_agent import (
    TrojanDeliveryBriefing,
    TrojanDeliveryIntelAgent,
)

__all__ = [
    "AIGenContentBriefing",
    "AIGenContentIntelAgent",
    "BECBriefing",
    "BECIntelAgent",
    "GeoBriefing",
    "GeoIntelAgent",
    "ImageRatioThresholds",
    "PhishBriefing",
    "PhishIntelAgent",
    "RansomwareBriefing",
    "RansomwareIntelAgent",
    "TimeAnomalyWindow",
    "TrojanDeliveryBriefing",
    "TrojanDeliveryIntelAgent",
]
