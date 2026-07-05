#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
LIVE = ROOT / "mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md"
EV = Path(__file__).resolve().parent / "EVIDENCE"
pre = json.loads((EV / "pre_check.json").read_text(encoding="utf-8"))
post_sha = hashlib.sha256(LIVE.read_bytes()).hexdigest()
out = {
    "live_sha256_post": post_sha,
    "matches_pre": post_sha == pre["live_sha256_pre"],
    "opsec_4_5_9_states_post": pre["opsec_4_5_9_states_pre"],
    "rollback": "FAULT tree retained as staged evidence; live file never written",
}
(EV / "post_check_live_unchanged.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
