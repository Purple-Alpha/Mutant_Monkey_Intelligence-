"""Phase 1.4 reserved policy parameter keys.

Per Matt's 2026-05-21 §11 decision 2 (the Phase 1.4 Mutation Engine
Specialisation lockdown), ``ProductionPolicyState.parameters`` is a
closed-set dictionary. Only the four keys listed here may appear in a
signed ``POLICY_UPDATE`` payload's ``parameters`` dict, in the
``requested_parameters`` kwarg of ``apply_signed_policy``, or in the
persisted state file:

* ``confidence_boost`` — Month 0 legacy; consumed by
  ``core/production/loop.py::_detect`` to nudge the deterministic
  prototype detector's confidence.
* ``fraud_risk_floor_lift`` — Phase 1.4 ``fraud_pattern_threshold``
  mutation; integer additive lift (0–25) on the precursor floor only
  when the LLM-derived fraud signal is already ``>= 40``.
* ``attachment_risk_floor_lift`` — Phase 1.4
  ``attachment_classifier_boost`` mutation; integer additive lift
  (0–25) on ``EmailAnalysisRansomwarePrecursorAnalysis.attachment_risk_score``
  through the precursor overlay.
* ``url_obfuscation_floor_lift`` — Phase 1.4
  ``url_obfuscation_sensitivity`` mutation; integer additive lift
  (0–25) on ``EmailAnalysisRansomwarePrecursorAnalysis.url_obfuscation_score``
  through the precursor overlay.

The reservation is enforced at **both** boundaries per Matt's §11
decision 2 tightening:

1. ``core/policy/pipeline.py::run_policy_promotion_cycle`` writes a
   sandbox-side REJECTED ``audit_verdict`` and refuses to emit the
   production-side audit + workflow_trigger when a signed
   ``POLICY_UPDATE`` carries an unauthorized key. Defense in depth:
   the unauthorized key never crosses the production boundary.
2. ``core/production_state/gate.py::apply_signed_policy`` raises
   ``GovernanceError("unauthorized parameter key: ...")`` at apply
   time on both the signed ``parameters`` and the caller's
   ``requested_parameters`` kwarg.

Adding a new key requires editing this module, the Phase 1.4 deep dive
(``4. Product_Roadmap/Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md``),
and pinning a new gate test. The frozen set guarantees the runtime can
never silently accept a freeform key.
"""

from __future__ import annotations

RESERVED_PARAMETER_KEYS: frozenset[str] = frozenset(
    {
        "confidence_boost",
        "fraud_risk_floor_lift",
        "attachment_risk_floor_lift",
        "url_obfuscation_floor_lift",
    }
)


def unauthorized_parameter_keys(parameters: dict[str, object]) -> tuple[str, ...]:
    """Return the sorted tuple of keys in ``parameters`` that are NOT reserved.

    Helper so callers (gate + promotion pipeline) can produce a stable,
    sorted diagnostic listing in their rejection findings/messages
    without each layer reimplementing the same ``set - set`` math.
    """

    unauthorized = set(parameters.keys()) - RESERVED_PARAMETER_KEYS
    return tuple(sorted(unauthorized))


__all__ = [
    "RESERVED_PARAMETER_KEYS",
    "unauthorized_parameter_keys",
]
