#!/usr/bin/env python3
"""
Mirror Dimension Router CLI — route hostile payloads to cryptolalia tarpit (chaos lab only).

See: mmi/project_brain/chaos/MMI_MIRROR_DIMENSION_ROUTER_SPEC_2026-07.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_LAB_ROOT = Path("/tmp/mmi_chaos_lab")
DEFAULT_AUTHORITY = Path("/mnt/c/MMI")
CHAOS_DIR = DEFAULT_AUTHORITY / "mmi/project_brain/chaos"

if CHAOS_DIR.exists() and str(CHAOS_DIR) not in sys.path:
    sys.path.insert(0, str(CHAOS_DIR))

from mirror_dimension_router import MirrorDimensionRouter  # type: ignore


def mirror_root_for_lab(lab_root: Path, lab_id: str) -> Path:
    return lab_root / lab_id / "MIRROR"


def main() -> int:
    parser = argparse.ArgumentParser(description="MMI Mirror Dimension Router — chaos lab only")
    parser.add_argument("--lab-root", type=Path, default=DEFAULT_LAB_ROOT)
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--canary-key", default="CANARY-MMI-CHAOS-LAB-NOT-REAL")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_route = sub.add_parser("route", help="critic + route payload to mirror tarpit")
    p_route.add_argument("--lab-id", required=True)
    p_route.add_argument("--agent-id", required=True)
    p_route.add_argument("--payload", help="inline hostile payload string")
    p_route.add_argument("--payload-file", type=Path, help="read payload from file")

    p_status = sub.add_parser("status", help="contained cells index")
    p_status.add_argument("--lab-id", required=True)

    p_harvest = sub.add_parser("harvest", help="telemetry for evidence hub / dashboard")
    p_harvest.add_argument("--lab-id", required=True)
    p_harvest.add_argument("--agent-id", required=True)

    args = parser.parse_args()
    mirror_root = mirror_root_for_lab(args.lab_root, args.lab_id)
    MirrorDimensionRouter.assert_not_authority_path(mirror_root, args.authority)
    router = MirrorDimensionRouter(mirror_root, canary_key=args.canary_key)

    if args.cmd == "route":
        if args.payload_file:
            payload = args.payload_file.read_text(encoding="utf-8")
        elif args.payload:
            payload = args.payload
        else:
            raise SystemExit("route requires --payload or --payload-file")
        result = router.route_to_mirror(args.agent_id, payload)
        print(json.dumps(result, indent=2))
        return 0 if result.get("routed") else 1

    if args.cmd == "status":
        print(json.dumps(router.ecosystem_status(), indent=2))
        return 0

    if args.cmd == "harvest":
        print(json.dumps(router.harvest_exploit_telemetry(args.agent_id), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
