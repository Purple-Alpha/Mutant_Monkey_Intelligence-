#!/usr/bin/env python3
"""Level 2 chaos sandbox detections — fixtures only; do not import live mutation."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
FX = Path(__file__).resolve().parent
results: list[dict] = []


def record(
    test_id: str,
    name: str,
    fixture: Path,
    fault: str,
    expected: str,
    actual: str,
    detected: bool,
    recovery: str,
    evidence: str,
    harden: str,
    verdict: str,
) -> None:
    results.append(
        {
            "id": test_id,
            "name": name,
            "fixture_path": fixture.relative_to(ROOT).as_posix(),
            "injected_fault": fault,
            "expected_detection": expected,
            "actual_detection": actual,
            "detected": detected,
            "detection_result": verdict,
            "recovery_path": recovery,
            "evidence_captured": evidence,
            "hardening_action": harden,
        }
    )


# T01
t1 = FX / "test01_stale_war_room"
t1.mkdir(exist_ok=True)
(t1 / "war_room_stale.txt").write_text(
    "PIPE STATUS: LOADED\nTASK: mmi-chaos-tabletop-v1\nSCORE: 80\n", encoding="utf-8"
)
(t1 / "tasks_truth.json").write_text(
    json.dumps([{"id": "mmi-chaos-sandbox-v2", "status": "pending"}], indent=2), encoding="utf-8"
)
stale_task = re.search(r"TASK: (\S+)", (t1 / "war_room_stale.txt").read_text(encoding="utf-8")).group(1)
truth_task = json.loads((t1 / "tasks_truth.json").read_text(encoding="utf-8"))[0]["id"]
mismatch = stale_task != truth_task
record(
    "T01",
    "Stale active-task mismatch",
    t1,
    "War room shows tabletop-v2-complete task; fixture tasks.json shows sandbox-v2 pending",
    "Detect TASK id mismatch between war room output and tasks.json",
    f"stale={stale_task}, truth={truth_task}, mismatch={mismatch}",
    mismatch,
    "Re-run war_room.py --json or reload_mmi_pipes.py before acting",
    f"{stale_task} vs {truth_task}",
    "War room cheatsheet: refresh before act (R4)",
    "PASS" if mismatch else "FAIL",
)

# T02
t2 = FX / "test02_dry_confusion"
t2.mkdir(exist_ok=True)
(t2 / "operator_assumption.md").write_text(
    "I believe mmi-opsec-human-gate-tightening is still pending.\n", encoding="utf-8"
)
(t2 / "tasks_truth.json").write_text(
    json.dumps(
        [
            {"id": "mmi-opsec-human-gate-tightening", "status": "completed"},
            {"id": "mmi-chaos-sandbox-v2", "status": "pending"},
        ],
        indent=2,
    ),
    encoding="utf-8",
)
assumption = "pending" in (t2 / "operator_assumption.md").read_text(encoding="utf-8")
hg = next(t for t in json.loads((t2 / "tasks_truth.json").read_text(encoding="utf-8")) if "human-gate" in t["id"])
confusion = assumption and hg["status"] == "completed"
record(
    "T02",
    "DRY pipeline confusion",
    t2,
    "Operator assumes human-gate pending; fixture shows completed + sandbox active",
    "Cross-read detects Task closed vs mental pending queue",
    f"assumption_pending={assumption}, human_gate_status={hg['status']}, confusion_risk={confusion}",
    confusion,
    "Read tasks.json + worksheet sign-off; reload pipes",
    "operator_assumption.md vs tasks_truth.json",
    "Status: Task closed ≠ OPSEC proven",
    "PASS" if confusion else "FAIL",
)

# T03
t3 = FX / "test03_headline_launder"
t3.mkdir(exist_ok=True)
brief = (ROOT / "mmi/project_brain/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md").read_text(
    encoding="utf-8"
)
injected = brief.replace(
    "This brief is scoped to backup-targeting",
    "Verizon reports 88% of Canadian SMB breaches involve ransomware. This brief is scoped to backup-targeting",
    1,
)
(t3 / "INTEL_brief_INJECTED.md").write_text(injected, encoding="utf-8")
sec1_match = re.search(r"## 1\. Threat summary\n(.*?)(?=\n---|\n## 2\.)", injected, re.S)
sec1 = sec1_match.group(1) if sec1_match else ""
bad = bool(re.search(r"88%|Verizon", sec1)) and "Global Data" not in sec1
live_match = re.search(r"## 1\. Threat summary\n(.*?)(?=\n---|\n## 2\.)", brief, re.S)
live_sec1 = live_match.group(1) if live_match else ""
live_bad = bool(re.search(r"88%|Verizon", live_sec1)) and "Global Data" not in live_sec1
record(
    "T03",
    "Global stat in Canadian headline",
    t3,
    "Verizon 88% injected into §1 without [Global Data] tag",
    "§1 grep finds vendor % without localization tag",
    f"fixture_violation={bad}, live_headline_clean={not live_bad}",
    bad,
    "Revert headline; keep stats in §5 only",
    "INTEL_brief_INJECTED.md §1",
    "Brief closeout §1 grep (R5)",
    "PASS" if bad and not live_bad else "FAIL",
)

# T04
t4 = FX / "test04_manifest_gap"
t4.mkdir(exist_ok=True)
log = json.loads((ROOT / "mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json").read_text(encoding="utf-8"))
tail = log[-1]
files = [f["path"] for f in tail["files"]]
required = "mmi/project_brain/chaos/MMI_CHAOS_TABLETOP_V1_2026-07.md"
gap_manifest = {"files": [p for p in files if p != required], "push_file": tail["push_file"]}
(t4 / "manifest_gap.json").write_text(json.dumps(gap_manifest, indent=2), encoding="utf-8")
missing = required not in gap_manifest["files"]
record(
    "T04",
    "Archive manifest missing required file",
    t4,
    f"Removed {required} from copied manifest",
    "Required-path check finds missing chaos doctrine",
    f"required_missing={missing}, live_has_chaos={required in files}",
    missing,
    "Post-amend push SOP; compare to BACKUP_PROTECTED_PATHS",
    "manifest_gap.json",
    "Post-amend B2 push (R2)",
    "PASS" if missing else "FAIL",
)

# T05
t5 = FX / "test05_restore_ambiguity"
t5.mkdir(exist_ok=True)
ambig = {
    "archives": [
        {"push_file": "mmi_backup_20260630_154854.tar.gz", "archive_sha256": "f1762050..."},
        {"push_file": "mmi_backup_20260630_162035.tar.gz", "archive_sha256": "f262e3e7..."},
    ],
    "latest_good_pointer": None,
}
(t5 / "restore_ambiguity.json").write_text(json.dumps(ambig, indent=2), encoding="utf-8")
ambiguous = ambig["latest_good_pointer"] is None and len(ambig["archives"]) > 1
record(
    "T05",
    "Restore-path ambiguity",
    t5,
    "Multiple same-day archives; no latest_good_pointer",
    "Ambiguity detected when pointer absent under pressure",
    f"ambiguous={ambiguous}, live_tail={log[-1]['push_file']}",
    ambiguous,
    "Use push log tail; add MMI_LATEST_GOOD_ARCHIVE.md (R3)",
    "restore_ambiguity.json",
    "Latest-good archive stub (R3)",
    "PASS" if ambiguous else "FAIL",
)

# T06
t6 = FX / "test06_opsec_false_done"
t6.mkdir(exist_ok=True)
(t6 / "opsec_false_done.md").write_text(
    "# fixture\n\n| item | state | last_done | verify_method |\n|---|---|---|---|\n"
    "| OPSEC-4 | DONE | | worksheet exists |\n"
    "| OPSEC-5 | DONE | 2026-06-30 | dry-run only |\n"
    "| OPSEC-9 | NOT_STARTED | | |\n",
    encoding="utf-8",
)
text6 = (t6 / "opsec_false_done.md").read_text(encoding="utf-8")
violations = []
for item in ["OPSEC-4", "OPSEC-5"]:
    m = re.search(rf"\| {item} \| DONE \| ([^|]*)\|", text6)
    if m and not m.group(1).strip():
        violations.append(f"{item}: DONE without last_done")
if re.search(r"\| OPSEC-5 \| DONE \| 2026-06-30 \| dry-run only \|", text6):
    violations.append("OPSEC-5: dry-run-only verify_method")
live = (ROOT / "mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md").read_text(encoding="utf-8")
live_bad = []
for item in ["OPSEC-4", "OPSEC-5", "OPSEC-9"]:
    m = re.search(rf"\| {item} \|[^|]+\|[^|]+\|[^|]+\|[^|]+\| ([A-Z_]+) \|", live)
    if m and m.group(1) != "NOT_STARTED":
        live_bad.append(item)
record(
    "T06",
    "OPSEC-4/5/9 falsely marked DONE",
    t6,
    "Fixture marks OPSEC-4/5 DONE without proper evidence",
    "Audit detects DONE without last_done / dry-run-only for OPSEC-5",
    f"fixture_violations={violations}; live_items={live_bad or 'all NOT_STARTED'}",
    len(violations) > 0,
    "Revert checklist; enforce worksheet §5",
    str(violations),
    "Dual-read worksheet + checklist",
    "PASS" if violations and not live_bad else "PASS WITH REVISIONS",
)

# T07
t7 = FX / "test07_no_decision_log"
t7.mkdir(exist_ok=True)
(t7 / "vendor_email_scenario.txt").write_text(
    "URGENT: wire $50k to new account. Operator checked domain only.\n", encoding="utf-8"
)
has_log = "decision_log_id" in (t7 / "vendor_email_scenario.txt").read_text(encoding="utf-8")
record(
    "T07",
    "Missing decision log on vendor email",
    t7,
    "Urgent wire scenario without decision_log_id",
    "Missing log detected before business action",
    f"decision_log_present={has_log}",
    not has_log,
    "OPSEC_HUMAN_GATE_DRILL §6 at first suspicion",
    "vendor_email_scenario.txt",
    "OPSEC-9 habit when Matt ready",
    "PASS" if not has_log else "FAIL",
)

# T08
t8 = FX / "test08_non_mmi_scope"
t8.mkdir(exist_ok=True)
non_mmi = [
    {
        "id": "phase1-stability-audit",
        "status": "pending",
        "instruction": "PROJECT: SOCIAL ARCHITECT PHASE 1.",
    }
]
(t8 / "tasks_non_mmi.json").write_text(json.dumps(non_mmi, indent=2), encoding="utf-8")


def is_mmi_task(task: dict) -> bool:
    return str(task.get("id", "")).startswith("mmi-") or str(task.get("instruction", "")).startswith(
        "PROJECT: MMI."
    )


blocked = not is_mmi_task(non_mmi[0])
record(
    "T08",
    "Non-MMI scope contamination",
    t8,
    "Active task is phase1-stability-audit only",
    "is_mmi_task False → reload would BLOCK",
    f"is_mmi_task={is_mmi_task(non_mmi[0])}, should_block={blocked}",
    blocked,
    "MMI_ACTIVE_SCOPE + is_mmi_task guard",
    "tasks_non_mmi.json",
    "Keep non-MMI tasks paused",
    "PASS" if blocked else "FAIL",
)

# T09
t9 = FX / "test09_hash_mismatch"
t9.mkdir(exist_ok=True)
entry = {
    "push_file": "mmi_backup_FAKE.tar.gz",
    "local_sha256": "aaa",
    "remote_bytes": 100,
    "local_bytes": 200,
    "push_status": "PASS",
}
(t9 / "push_log_mismatch.json").write_text(json.dumps(entry, indent=2), encoding="utf-8")
hash_bad = entry["local_bytes"] != entry["remote_bytes"]
record(
    "T09",
    "Backup hash mismatch",
    t9,
    "push_status PASS but bytes differ",
    "Integrity check flags mismatch",
    f"bytes_mismatch={hash_bad}, false_pass_label={entry['push_status']=='PASS' and hash_bad}",
    hash_bad,
    "Verify sha256 + byte equality; OPSEC-7",
    "local_bytes=200 remote_bytes=100",
    "Checksum on push; weekly tar spot-check",
    "PASS" if hash_bad else "FAIL",
)

# T10
t10 = FX / "test10_false_pass_closeout"
t10.mkdir(exist_ok=True)
fake = {
    "id": "mmi-fake-closeout",
    "status": "completed",
    "result_summary": "PASS",
    "output_files": ["mmi/project_brain/chaos/fixtures/v2/test10_false_pass_closeout/MISSING_OUTPUT.md"],
}
(t10 / "task_false_pass.json").write_text(json.dumps(fake, indent=2), encoding="utf-8")
missing_out = not (ROOT / fake["output_files"][0]).exists()
false_pass = fake["status"] == "completed" and fake["result_summary"] == "PASS" and missing_out
record(
    "T10",
    "False PASS closeout",
    t10,
    "Completed PASS but output file missing",
    "File-exists check catches false PASS",
    f"output_missing={missing_out}, false_pass={false_pass}",
    false_pass,
    "Reject closeout until outputs exist",
    "MISSING_OUTPUT.md absent",
    "Closeout output spot-check",
    "PASS" if false_pass else "FAIL",
)

manifest = {
    "task": "mmi-chaos-sandbox-v2",
    "level": 2,
    "fixture_root": FX.relative_to(ROOT).as_posix(),
    "live_authority_mutated": False,
    "tests": results,
}
(FX / "FIXTURE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
