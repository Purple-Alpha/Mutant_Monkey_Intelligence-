#!/usr/bin/env python3
"""L3-04 fixture setup — staged intel brief copy only; live briefs not modified."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
BRIEF = ROOT / "mmi/project_brain/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md"
BRIEF2 = ROOT / "mmi/project_brain/intel/briefs/INTEL_polymorphic-ransomware-delivery_2026-07.md"
FX = Path(__file__).resolve().parent
BEFORE = FX / "BEFORE/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md"
FAULT = FX / "FAULT/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md"
EV = FX / "EVIDENCE"

INJECT = (
    "Verizon reports 88% of Canadian SMB breaches involve ransomware. "
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for d in (BEFORE.parent, FAULT.parent, EV):
        d.mkdir(parents=True, exist_ok=True)

    shutil.copy2(BRIEF, BEFORE)
    shutil.copy2(BRIEF, FAULT)
    text = FAULT.read_text(encoding="utf-8")
    needle = (
        "For a solo Canadian operator running a local-first stack "
        "(`tasks.json` + `mmi/project_brain/` + B2 cold mirror), the failure mode is not only "
        "host encryption — it is **loss of the last known-good offline copy** or an "
        "**unverified restore path**.\n\n"
    )
    if needle not in text:
        raise SystemExit("inject anchor not found in brief")
    text = text.replace(needle, needle + INJECT + "\n")
    FAULT.write_text(text, encoding="utf-8")

    pre = {
        "live_briefs": {
            BRIEF.relative_to(ROOT).as_posix(): sha256(BRIEF),
            BRIEF2.relative_to(ROOT).as_posix(): sha256(BRIEF2),
        },
        "injected_fault": INJECT.strip(),
        "before_copy": BEFORE.relative_to(ROOT).as_posix(),
        "fault_copy": FAULT.relative_to(ROOT).as_posix(),
    }
    (EV / "pre_check.json").write_text(json.dumps(pre, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(pre, indent=2))


if __name__ == "__main__":
    main()
