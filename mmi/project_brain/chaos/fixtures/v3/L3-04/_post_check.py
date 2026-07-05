#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
EV = Path(__file__).resolve().parent / "EVIDENCE"
pre = json.loads((EV / "pre_check.json").read_text(encoding="utf-8"))

live_sha = {}
for rel in pre["live_briefs"]:
    p = ROOT / rel
    live_sha[rel] = hashlib.sha256(p.read_bytes()).hexdigest()

matches = all(live_sha[rel] == pre["live_briefs"][rel] for rel in pre["live_briefs"])

proc = subprocess.run(
    [sys.executable, str(ROOT / "scripts/mmi_verify.py"), "intel-briefs"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
live_scan = json.loads(proc.stdout) if proc.stdout.strip() else {"error": proc.stderr}

out = {
    "live_briefs_sha256_post": live_sha,
    "matches_pre": matches,
    "live_intel_briefs_scan": live_scan,
    "live_scan_ok": live_scan.get("ok") is True and proc.returncode == 0,
    "rollback": "FAULT tree retained as staged evidence; live briefs never written",
}
(EV / "post_check_live_unchanged.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
sys.exit(0 if matches and out["live_scan_ok"] else 1)
