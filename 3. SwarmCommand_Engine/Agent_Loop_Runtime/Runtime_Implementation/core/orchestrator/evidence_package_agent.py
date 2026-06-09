"""Evidence Package governed-agent wrapper - swarm agent #46.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Evidence_Package_Agent_Design_Contract_Deep_Dive.md`` (2026-06-08). It is the
first Layer 4 Evidence agent on the swarm scoreboard. It wraps the existing
signed Pass 1 package assembler
``core.evidence_package.generate_package_from_test_plan`` and exposes it as an
explicitly wired governed agent on the proven ``Agent`` protocol ->
``AgentContribution`` -> ``DecisionEvidenceRecord`` path already used by the
Detection-layer agents.

Scope / governance boundary (contract D1-D10, deliberate):
- D2 generator immutability: this wrapper changes no package-generation
  behaviour, gate, schema, render, redaction rule, boundary statement,
  audit-packet coverage rule, or done criterion. The generator is injected and
  called read-only; the wrapper derives facts from its return value only.
- D3 builder/auditor separation: the assembler is NOT the auditor. This wrapper
  never calls ``audit_package`` / ``make_xai_client`` (Grok), never renders the
  PDF, and never emits a done declaration. Audit/review remains the separate
  signed Layer 6 / package-auditor path (``final_review_001`` writes
  ``audit_record_id``; this agent cannot).
- D4 Stage 1 synthetic-only input surface: the wrapper assembles from one
  explicit synthetic/test-plan source directory supplied by the caller. No
  Blackboard email body and no real tenant data flow through it.
- D5 facts-only Layer 4 contribution: the contribution carries only safe package
  metadata (package id, version, gate-pass status, gate count, audit-packet
  coverage flag, markdown-bundle-present flag, is_done, record count) plus the
  closed ``control_mapping`` identifier and a bounded Stage 1 ``underwriter_note``.
  No package contents, raw source-record content, rendered Markdown, vendor /
  customer names, tenant secrets, signed-by values, or file bytes are emitted.
- D6 no buyer surface / no claims: Stage 1 produces internal synthetic evidence
  only. ``is_done`` is expected ``False`` and is surfaced as a fact, never as a
  completion claim.
- D5/D7 rollout: Evidence Stage 1 - intentionally NOT registered in
  ``build_default_registry``; wired only by explicit callers and tests until a
  separate Matt-signed Stage 2 promotion record (template §6.2).
- D8 Stage A / no autonomy: ``challenge`` returns ``None``;
  ``autonomous_action_allowed = False``; the wrapper authors no disposition.
- purity: the wrapper performs no network call and spawns no subprocess; it
  imports no runtime detector / scoring module.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Callable
from uuid import UUID

from core.blackboard import (
    AgentContributionPayload,
    Environment,
    GovernanceError,
)
from core.evidence_package import (
    EvidencePackageResult,
    generate_package_from_test_plan,
)
from core.evidence_package.package_generator import PACKAGE_VERSION

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, submit_agent_contribution

EVIDENCE_PACKAGE_AGENT_ID = "evidence_package_001"
EVIDENCE_PACKAGE_LAYER = 4  # Evidence
EVIDENCE_PACKAGE_AUTHORITY_LEVEL = 3  # Specialist Agent

# D5 closed control-surface identifier - a stable label for the one control
# surface this package evidences. Not a claim; <=160 chars.
CONTROL_MAPPING = "cyber_insurance_evidence_package_v1:email_fraud_inbox_mdr"

# D5/D6 bounded Stage 1 note. Factual, no forbidden-language claim; <=160 chars.
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic evidence package; not buyer-released, "
    "not audited, not a done declaration."
)

PackageGenerator = Callable[..., EvidencePackageResult]


def digest_package_request(
    *,
    source_dir: Path,
    output_root: Path,
    tenant_id: str,
    trigger: str,
) -> str:
    """Deterministic SHA-256 digest of one package-assembly request.

    Stable for the same source dir / output root / tenant / trigger so the
    ``MissionContext.inputs_digest`` does not depend on wall-clock time.
    """

    raw = "|".join(
        [str(Path(source_dir)), str(Path(output_root)), tenant_id, trigger]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _package_facts(result: EvidencePackageResult) -> tuple[str, ...]:
    """Derive the facts-only Layer 4 metadata tuple from a package result.

    Closed key set; values are identifiers and boolean/count status only. No
    package contents, render text, source-record content, or file bytes.
    """

    records_dir = result.package_dir / "records"
    record_count = (
        len(list(records_dir.glob("*.json"))) if records_dir.exists() else 0
    )
    return (
        f"package_id={result.package_id}",
        f"package_version={PACKAGE_VERSION}",
        f"gates_passed={str(result.gates_passed).lower()}",
        f"gate_count={len(result.gate_results)}",
        f"audit_packet_coverage_complete="
        f"{str(result.audit_packet_coverage_complete).lower()}",
        f"markdown_bundle_present={str(result.markdown_bundle_path.exists()).lower()}",
        f"is_done={str(result.is_done).lower()}",
        f"record_count={record_count}",
    )


def contribution_payload_from(
    contribution: AgentContribution,
    *,
    case_id: UUID,
    inputs_digest: str,
) -> AgentContributionPayload:
    """Map an already-validated ``AgentContribution`` to its persistence payload."""

    return AgentContributionPayload(
        case_id=case_id,
        inputs_digest=inputs_digest,
        agent_id=contribution.agent_id,
        layer=contribution.layer,
        observed_facts=list(contribution.observed_facts),
        verification_source=contribution.verification_source,
        verification_outcome=contribution.verification_outcome,
        challenge_result=contribution.challenge_result,
        challenge_rationale=contribution.challenge_rationale,
        control_mapping=contribution.control_mapping,
        underwriter_note=contribution.underwriter_note,
    )


class EvidencePackageAgent:
    """Governed Layer 4 Evidence agent wrapping the Pass 1 package assembler."""

    agent_id: str = EVIDENCE_PACKAGE_AGENT_ID
    layer: int = EVIDENCE_PACKAGE_LAYER
    authority_level: int = EVIDENCE_PACKAGE_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        source_dir: Path,
        output_root: Path,
        tenant_id: str,
        trigger: str = "on_demand",
        now: datetime | None = None,
        environment: Environment = Environment.PRODUCTION,
        generator: PackageGenerator = generate_package_from_test_plan,
    ) -> None:
        self._source_dir = Path(source_dir)
        self._output_root = Path(output_root)
        self._tenant_id = tenant_id
        self._trigger = trigger
        self._now = now
        self._environment = environment
        # Injected so the read-only generator dependency is explicit and the
        # builder/auditor-separation + purity tests can substitute it.
        self._generator = generator

    def request_digest(self) -> str:
        return digest_package_request(
            source_dir=self._source_dir,
            output_root=self._output_root,
            tenant_id=self._tenant_id,
            trigger=self._trigger,
        )

    def assemble_package(self) -> EvidencePackageResult:
        """Run the signed Pass 1 assembler read-only over the synthetic source.

        D2: behaviour is the generator's; this wrapper adds no package logic.
        """

        return self._generator(
            source_dir=self._source_dir,
            output_root=self._output_root,
            tenant_id=self._tenant_id,
            trigger=self._trigger,
            now=self._now,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.assemble_package()
        # D6/D8 done-state guard: Stage 1 synthetic assembly is never "done".
        # If the Pass 1 result ever claims completion, fail closed rather than
        # emit a misleading evidence contribution.
        if result.is_done or result.done_declaration_path is not None:
            raise GovernanceError(
                "EvidencePackageAgent is Evidence Stage 1 (synthetic); it cannot "
                "emit a contribution for a package that claims a done declaration"
            )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=_package_facts(result),
            control_mapping=CONTROL_MAPPING,
            underwriter_note=STAGE1_UNDERWRITER_NOTE,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        # Evidence layer assembles; auditing/review is a separate layer.
        return None

    def persist_contribution(
        self,
        route_context: RouteContext,
        context: MissionContext,
        contribution: AgentContribution,
    ) -> RouteResult:
        """Write this agent's contribution via the approved registry-gated route."""

        payload = contribution_payload_from(
            contribution,
            case_id=context.case_id,
            inputs_digest=context.inputs_digest,
        )
        return submit_agent_contribution(
            route_context,
            tenant_id=context.tenant_id,
            environment=self._environment,
            source_agent=self.agent_id,
            payload=payload,
            parent_record_id=context.source_record_id,
        )
