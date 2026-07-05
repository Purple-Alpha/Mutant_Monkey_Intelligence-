from __future__ import annotations

from scripts.phase1_stability_harness import CANONICAL_STACK, EVIDENCE_FILES


def test_canonical_stack_includes_iceberg_ingress():
    assert "iceberg-ingress" in CANONICAL_STACK
    assert CANONICAL_STACK.index("iceberg-ingress") == 2
    assert "iceberg_ingress_summary.json" in EVIDENCE_FILES
