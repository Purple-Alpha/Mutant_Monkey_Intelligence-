"""Build the Acme MSP-facing Effective Parameter Report demo.

This operator-side script creates an isolated demo blackboard for the fictional
``acme-industries-demo`` tenant, seeds deterministic policy / override state,
and then invokes the real tenant override operator ``report`` command to render
the markdown report artifact.

It must stay outside ``core/`` because it writes demo data. It does not touch
any production tenant path unless an operator explicitly points it elsewhere.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

from core.production_state import (
    ProductionPolicyState,
    create_or_update_tenant_override,
    save_state,
    state_path,
)
from core.production_state.tenant_override_operator import run as run_operator_cli

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNTIME_ROOT = Path(__file__).resolve().parents[1]

DEMO_TENANT_ID = "acme-industries-demo"
DEMO_POLICY_VERSION = "acme-demo-policy-v1"
DEMO_EVALUATED_AT = datetime(2026, 5, 23, 15, 30, tzinfo=timezone.utc)
DEMO_EXPIRES_AT = DEMO_EVALUATED_AT + timedelta(days=30)
DEMO_SOURCE = "demo_effective_parameter_report_generator"

DEFAULT_DEMO_DIR = RUNTIME_ROOT / "demo_outputs" / "acme_effective_parameter_report"
DEFAULT_BLACKBOARD_ROOT = DEFAULT_DEMO_DIR / "blackboard"
DEFAULT_REPORT_OUT = (
    REPO_ROOT
    / "1. Business_Operations"
    / "Client_Documents"
    / "Generated"
    / "Acme_Effective_Parameter_Report_Demo.md"
)


def generate_demo_report(
    *,
    blackboard_root: Path = DEFAULT_BLACKBOARD_ROOT,
    out_path: Path = DEFAULT_REPORT_OUT,
    tenant_id: str = DEMO_TENANT_ID,
    evaluated_at: datetime = DEMO_EVALUATED_AT,
    reset_existing: bool = True,
) -> Path:
    """Seed deterministic demo state and render the report through the CLI."""

    if reset_existing and blackboard_root.exists():
        _remove_demo_blackboard(blackboard_root)

    _seed_signed_policy_state(blackboard_root=blackboard_root, tenant_id=tenant_id)
    _seed_override_audit_trail(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        evaluated_at=evaluated_at,
    )

    rc = run_operator_cli(
        [
            "--blackboard-root",
            str(blackboard_root),
            "--tenant-id",
            tenant_id,
            "--format",
            "markdown",
            "report",
            "--at",
            evaluated_at.isoformat(),
            "--audit-limit",
            "5",
            "--out",
            str(out_path),
        ]
    )
    if rc != 0:
        raise RuntimeError(f"tenant_override_operator report failed with exit code {rc}")
    return out_path


def _seed_signed_policy_state(*, blackboard_root: Path, tenant_id: str) -> None:
    """Write an isolated demo policy baseline.

    This is not a production policy write. The script uses a demo blackboard
    root and creates data solely for client-facing walkthrough artifacts.
    """

    save_state(
        state_path(blackboard_root, tenant_id),
        ProductionPolicyState(
            active_version=DEMO_POLICY_VERSION,
            parameters={
                "confidence_boost": 0.2,
                "fraud_risk_floor_lift": 5,
                "attachment_risk_floor_lift": 0,
                "url_obfuscation_floor_lift": 5,
                "vendor_invoice_recall_floor": "phase_1_5",
            },
        ),
    )


def _seed_override_audit_trail(
    *,
    blackboard_root: Path,
    tenant_id: str,
    evaluated_at: datetime,
) -> None:
    create_or_update_tenant_override(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        parameters={"attachment_risk_floor_lift": 12},
        reason="Initial pilot tuning for suspicious attachment-heavy invoices.",
        requested_by="msp_operator_jane",
        approved_by="msp_owner_dave",
        expires_at=DEMO_EXPIRES_AT,
        source=DEMO_SOURCE,
        now=evaluated_at - timedelta(minutes=30),
    )
    create_or_update_tenant_override(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        parameters={
            "fraud_risk_floor_lift": 10,
            "url_obfuscation_floor_lift": 8,
        },
        reason=(
            "Finance-heavy MSP pilot: raise invoice fraud and URL obfuscation "
            "review thresholds for the first 30 days."
        ),
        requested_by="msp_operator_jane",
        approved_by="msp_owner_dave",
        expires_at=DEMO_EXPIRES_AT,
        source=DEMO_SOURCE,
        now=evaluated_at - timedelta(minutes=15),
    )


def _remove_demo_blackboard(blackboard_root: Path) -> None:
    resolved = blackboard_root.resolve()
    allowed_root = DEFAULT_DEMO_DIR.resolve()
    if allowed_root != resolved and allowed_root not in resolved.parents:
        raise ValueError(
            "refusing to reset a blackboard outside the Acme demo output directory; "
            "delete custom paths manually or pass --keep-existing"
        )
    shutil.rmtree(resolved)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acme_effective_parameter_report_demo",
        description=(
            "Seed the Acme demo blackboard and render a real Effective Parameter "
            "Report through tenant_override_operator report."
        ),
    )
    parser.add_argument(
        "--blackboard-root",
        type=Path,
        default=DEFAULT_BLACKBOARD_ROOT,
        help=f"Demo blackboard root (default: {DEFAULT_BLACKBOARD_ROOT})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_REPORT_OUT,
        help=f"Markdown report output path (default: {DEFAULT_REPORT_OUT})",
    )
    parser.add_argument(
        "--tenant-id",
        default=DEMO_TENANT_ID,
        help=f"Demo tenant id (default: {DEMO_TENANT_ID})",
    )
    parser.add_argument(
        "--at",
        default=DEMO_EVALUATED_AT.isoformat(),
        help="Timezone-aware ISO datetime used for report evaluation.",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Do not reset existing demo blackboard data before seeding.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    evaluated_at = datetime.fromisoformat(args.at)
    if evaluated_at.tzinfo is None:
        raise SystemExit("--at must be timezone-aware")

    out_path = generate_demo_report(
        blackboard_root=args.blackboard_root,
        out_path=args.out,
        tenant_id=args.tenant_id,
        evaluated_at=evaluated_at,
        reset_existing=not args.keep_existing,
    )
    print(f"Generated Acme Effective Parameter Report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
