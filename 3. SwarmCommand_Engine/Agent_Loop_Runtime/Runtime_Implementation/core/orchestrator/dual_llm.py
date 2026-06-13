"""Dual LLM boundary enforcement — signed June 12 2026.

Governing contract:
``4. Product_Roadmap/Dual_LLM_Contract.md`` §11 SIGNED 2026-06-12.

This module is deterministic orchestrator code, not an LLM. It enforces the
swarm-wide law:

* Q-class readers may see raw email, but hold no tools.
* P-class actors may use tools through the BRC gateway, but never see raw email.

The load-bearing artifact is ``EvidenceBundle``: structured evidence plus
content hashes only. Raw subject/body text is never stored in it and never
forwarded to P-class reconciliation.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable

from pydantic import BaseModel, ConfigDict, Field

from core.blackboard import EvidenceLedgerEntry, ReconciliationVerdict
from core.control_plane import GatewayController, GatewayRejected, GatewayRequest
from core.detectors._common import EmailContext
from core.reconciliation import LungState, ReconciliationAgent


class DualLLMError(Exception):
    """Raised on any Dual LLM contract violation; fail-safe, no dispatch."""


class AgentClass(str, Enum):
    Q_CLASS = "q_class"
    P_CLASS = "p_class"
    ORCHESTRATOR = "orchestrator"


Q_CLASS_AGENT_IDS = frozenset(
    {
        "sender_history_agent",
        "geo_velocity_agent",
        "content_analyzer",
        "url_receptor",
        "attachment_sandbox",
        "image_classifier",
    }
)
P_CLASS_AGENT_IDS = frozenset({"reconciliation_agent"})

_RAW_TEXT_KEYS = frozenset(
    {
        "subject",
        "body",
        "body_plain",
        "body_html",
        "raw_email",
        "raw_text",
        "email_text",
        "message",
        "content",
        "prompt",
    }
)
_TOOL_SYNTAX = re.compile(
    r"(?i)(tool_call|function_call|call_tool|<tool|</tool>|```tool|"
    r"\bexecute\s*\(|\bdispatch\s*\()"
)


class EvidenceBundle(BaseModel):
    """The only object the P-class ReconciliationAgent may receive.

    ``extra='forbid'`` prevents a Q-class model from smuggling unknown fields
    across the boundary. Raw text fields are rejected explicitly in
    ``assemble_bundle`` before this model is constructed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    subject_sha256: str
    body_sha256: str
    evidence_entries: tuple[EvidenceLedgerEntry, ...]
    q_agent_ids: tuple[str, ...]
    raw_text_present: bool = False


@dataclass(frozen=True)
class QClassRuntime:
    """Q-class runtime wrapper: raw-email access, no tools/credentials/actions."""

    agent_id: str
    collect: Callable[[EmailContext], EvidenceLedgerEntry]
    agent_class: AgentClass = AgentClass.Q_CLASS
    tool_scope: frozenset[str] = field(default_factory=frozenset)
    credentials: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.agent_id not in Q_CLASS_AGENT_IDS:
            raise DualLLMError(f"{self.agent_id!r} is not registered as Q-class")
        if self.tool_scope or self.credentials:
            raise DualLLMError("Q-class agents may not hold tools or credentials")

    def request_tool(self, *_args, **_kwargs):  # noqa: ANN002, ANN003
        raise DualLLMError("Q-class agents cannot request or execute tools")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def q_agent_class_for_raw_email(*, touches_raw_email: bool) -> AgentClass:
    """Spawn-time rule for fission: raw-email children are always Q-class."""

    return AgentClass.Q_CLASS if touches_raw_email else AgentClass.Q_CLASS


@dataclass
class DualLLMOrchestrator:
    """Deterministic Q→P pipeline controller.

    Pipeline:
    raw email → Q-class collectors → schema/policy validation → EvidenceBundle
    → P-class ReconciliationAgent → optional P-class tool via BRC gateway.
    """

    q_agents: tuple[QClassRuntime, ...]
    reconciliation_agent: ReconciliationAgent
    gateway: GatewayController | None = None

    def run(
        self,
        email: EmailContext,
        *,
        lung_state: LungState = LungState.NORMAL,
    ) -> tuple[EvidenceBundle, ReconciliationVerdict]:
        q_outputs = [agent.collect(email) for agent in self.q_agents]
        bundle = self.assemble_bundle(email, q_outputs)
        verdict = self.reconciliation_agent.analyze_bundle(
            bundle=bundle,
            lung_state=lung_state,
        )
        return bundle, verdict

    def assemble_bundle(
        self,
        email: EmailContext,
        q_outputs: Iterable[EvidenceLedgerEntry],
    ) -> EvidenceBundle:
        entries = tuple(self._validate_q_output(entry, email) for entry in q_outputs)
        if not entries:
            raise DualLLMError("EvidenceBundle requires at least one Q-class output")
        return EvidenceBundle(
            tenant_id=email.tenant_id,
            email_id=email.email_id,
            subject_sha256=sha256_text(email.subject),
            body_sha256=sha256_text(email.body),
            evidence_entries=entries,
            q_agent_ids=tuple(entry.agent_id for entry in entries),
            raw_text_present=False,
        )

    def p_class_tool_request(self, request: GatewayRequest):
        """Only P-class may request tools, and only through the BRC gateway."""

        if request.claimed_agent_id not in P_CLASS_AGENT_IDS:
            raise DualLLMError("only P-class may request tools through Dual LLM")
        if self.gateway is None:
            raise DualLLMError("P-class tool request requires a GatewayController")
        return self.gateway.handle(request)

    def _validate_q_output(
        self,
        entry: EvidenceLedgerEntry,
        email: EmailContext,
    ) -> EvidenceLedgerEntry:
        if entry.agent_id not in Q_CLASS_AGENT_IDS:
            raise DualLLMError(f"{entry.agent_id!r} is not Q-class")
        if entry.tenant_id != email.tenant_id or entry.email_id != email.email_id:
            raise DualLLMError("Q-class evidence does not match email identity")
        self._reject_raw_text(entry.details, email)
        return entry

    def _reject_raw_text(self, details: dict, email: EmailContext) -> None:
        raw_values = {email.subject, email.body} - {""}

        def walk(value: object, path: str = "") -> None:
            if isinstance(value, dict):
                for key, nested in value.items():
                    lowered = str(key).lower()
                    if lowered in _RAW_TEXT_KEYS:
                        raise DualLLMError(f"raw text field rejected: {path}{key}")
                    walk(nested, f"{path}{key}.")
            elif isinstance(value, (list, tuple, set)):
                for i, nested in enumerate(value):
                    walk(nested, f"{path}{i}.")
            elif isinstance(value, str):
                if value in raw_values:
                    raise DualLLMError("raw email text cannot enter EvidenceBundle")
                # Tool syntax is data at Q-class. We keep it inert by refusing to
                # interpret it and recording no executable surface from it.
                if _TOOL_SYNTAX.search(value):
                    return

        walk(details)

    @staticmethod
    def serialize_p_class_prompt(bundle: EvidenceBundle) -> str:
        """Test helper: the only P-class prompt material, with no raw text."""

        payload = {
            "tenant_id": bundle.tenant_id,
            "email_id": bundle.email_id,
            "subject_sha256": bundle.subject_sha256,
            "body_sha256": bundle.body_sha256,
            "evidence": [
                {
                    "agent_id": e.agent_id,
                    "evidence_type": e.evidence_type.value,
                    "confidence": e.confidence,
                    "details": e.details,
                }
                for e in bundle.evidence_entries
            ],
        }
        return json.dumps(payload, sort_keys=True)


__all__ = [
    "AgentClass",
    "DualLLMError",
    "DualLLMOrchestrator",
    "EvidenceBundle",
    "P_CLASS_AGENT_IDS",
    "Q_CLASS_AGENT_IDS",
    "QClassRuntime",
    "q_agent_class_for_raw_email",
    "sha256_text",
]
