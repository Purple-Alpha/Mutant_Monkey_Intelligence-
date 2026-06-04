"""Generate an internal Cyber Insurance Evidence Package Markdown bundle."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from core.evidence_package import generate_package_from_test_plan

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SOURCE_DIR = REPO_ROOT / "audit_outputs" / "cyber_insurance_v1_test_plan" / "stage_a_vendor_payment_redirect_001"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "audit_outputs" / "cyber_insurance_packages"

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = generate_package_from_test_plan(source_dir=args.source_dir, output_root=args.output_root, tenant_id=args.tenant, trigger=args.trigger, now=args.generated_at)
    print(f"package_id={result.package_id}")
    print(f"package_dir={result.package_dir}")
    print(f"markdown_bundle={result.markdown_bundle_path}")
    print(f"gates_passed={result.gates_passed}")
    for gate in result.gate_results:
        print(f"gate.{gate.gate}={'pass' if gate.passed else 'fail'}")
    return 0 if result.gates_passed else 2

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tenant", required=True, help="Tenant id for the package.")
    parser.add_argument("--trigger", choices=("quarterly", "on_demand", "annual"), default="on_demand", help="Generation trigger recorded in manifest.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR, help="Directory containing the five section 14 source artifacts.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Package output root. Defaults to audit_outputs/cyber_insurance_packages.")
    parser.add_argument("--generated-at", type=_parse_generated_at, default=None, help="Optional ISO timestamp for deterministic local/test runs.")
    return parser.parse_args(argv)

def _parse_generated_at(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

if __name__ == "__main__":
    raise SystemExit(main())
