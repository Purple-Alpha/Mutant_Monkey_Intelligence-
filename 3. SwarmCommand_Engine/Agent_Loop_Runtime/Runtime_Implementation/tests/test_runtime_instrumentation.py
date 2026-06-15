"""Runtime instrumentation tests.

The build is instrumentation-only: it may measure existing paths and write local
telemetry, but it must not change agent schemas, blackboard models, or create new
LLM calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from instrumentation.models import PipelineTelemetryRecord, TelemetryAggregateReport
from instrumentation.runtime import CATEGORIES, parse_model_rates, run_corpus


def test_runtime_instrumentation_single_category_outputs_trace(tmp_path: Path):
    report, output_dir = run_corpus(
        category="high_complexity_adversarial",
        count=2,
        output_root=tmp_path / "runs",
    )

    assert isinstance(report, TelemetryAggregateReport)
    assert report.email_count == 2
    assert report.worst_case_email_id.startswith("high_complexity_adversarial-")

    trace = output_dir / "worst_case_traces" / "high_complexity_adversarial_worst_case.txt"
    assert trace.exists()
    text = trace.read_text(encoding="utf-8")
    assert "RUN:" in text
    assert "reconciliation_agent" in text
    assert "verdict_written" in text

    per_email = sorted((output_dir / "per_email").glob("*_telemetry.json"))
    assert len(per_email) == 2
    record = PipelineTelemetryRecord.model_validate_json(per_email[0].read_text())
    assert record.agent_count == 6
    assert "content_analyzer" in record.agents_invoked
    assert record.total_pipeline_ms >= record.reconciliation_ms
    assert record.peak_memory_mb >= 0.0


def test_runtime_instrumentation_all_categories_are_synthetic(tmp_path: Path):
    for category in CATEGORIES:
        report, output_dir = run_corpus(category=category, count=1, output_root=tmp_path / "runs")
        assert report.corpus_category == category
        trace = output_dir / "worst_case_traces" / f"{category}_worst_case.txt"
        assert trace.exists()


def test_model_rates_are_config_driven(tmp_path: Path):
    rates_path = tmp_path / "rates.yaml"
    rates_path.write_text(
        "model-a:\n  input_per_1k_usd: 0.1\n  output_per_1k_usd: 0.2\n",
        encoding="utf-8",
    )
    assert parse_model_rates(rates_path) == {
        "model-a": {"input_per_1k_usd": 0.1, "output_per_1k_usd": 0.2}
    }


def test_instrumentation_does_not_modify_forbidden_schema_modules():
    instrumentation_files = {
        path.name for path in (REPO_ROOT / "instrumentation").glob("*.py")
    }
    assert instrumentation_files == {"__init__.py", "models.py", "runtime.py", "run_instrumentation.py"}

    forbidden_paths = [
        "core/orchestrator/agent_contract.py",
        "core/orchestrator/dual_llm.py",
        "core/blackboard/models.py",
        "core/blackboard/canonical_ledger.py",
        "core/blackboard/verdict_ledger.py",
    ]
    for forbidden in forbidden_paths:
        assert not (REPO_ROOT / "instrumentation" / forbidden).exists()

