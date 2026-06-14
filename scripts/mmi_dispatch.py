#!/usr/bin/env python3
import os
import re
import subprocess
import sys

REPO = "/home/socialarchitect/northstar"

# Supersession rules: a concept doc is considered satisfied when every mapped
# contract filename exists AND is SIGNED, even if no single contract filename
# contains the concept's literal name string. This covers concepts that were
# split across multiple signed contracts (e.g. Agent Fission -> Load + Specialisation).
CONCEPT_SUPERSESSION = {
    "Agent_Fission_Concept_Doc.md": [
        "Load_Fission_Contract_v2.md",
        "Specialisation_Fission_Contract_v2.md",
    ],
}

def read_file(path):
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        return None
    with open(full, encoding="utf-8") as f:
        return f.read()

def is_contract_signed(filename):
    """A contract counts as signed when a **Status:** line says SIGNED and not UNSIGNED/DRAFT."""
    content = read_file(os.path.join("4. Product_Roadmap", filename))
    if not content:
        return False
    for line in content.splitlines():
        if "**Status:**" not in line:
            continue
        if "UNSIGNED" in line or "DRAFT - unsigned" in line:
            continue
        if "SIGNED" in line:
            return True
    return False

def get_signed_unbuilt():
    scoreboard = read_file("agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md")
    if not scoreboard:
        return []
    matches = []
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        runtime_status = parts[2].strip("`")
        if runtime_status.startswith("SIGNED_UNBUILT"):
            name = parts[1] if len(parts) > 1 else line[:60]
            matches.append(name.strip())
    return matches

def get_awaiting_audit():
    """Rows whose runtime status starts AWAITING_AUDIT: built + tested, not yet
    gated. This is the lifecycle state between SIGNED_UNBUILT and GATED — the
    point at which MMI routes the work to the Grok completion gate.
    """
    scoreboard = read_file("agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md")
    if not scoreboard:
        return []
    matches = []
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        runtime_status = parts[2].strip("`")
        if runtime_status.startswith("AWAITING_AUDIT"):
            name = parts[1] if len(parts) > 1 else line[:60]
            matches.append(name.strip())
    return matches

def audit_task_slug(name):
    """Stable task id for the Grok gate manifest, derived from the row name.
    e.g. 'Safe-Stop State Machine' -> 'safe_stop_state_machine'.
    """
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")

def get_next_concept_without_contract():
    roadmap = os.path.join(REPO, "4. Product_Roadmap")
    if not os.path.exists(roadmap):
        return None
    concepts = [f for f in os.listdir(roadmap) if "Concept_Doc" in f]
    contracts = [f for f in os.listdir(roadmap) if "Contract" in f]
    for concept in sorted(concepts):
        superseding = CONCEPT_SUPERSESSION.get(concept)
        if superseding and all(
            c in contracts and is_contract_signed(c) for c in superseding
        ):
            continue
        name = concept.replace("_Concept_Doc.md", "").replace("_", "")
        if not any(name in contract.replace("_", "") for contract in contracts):
            return concept
    return None

def get_pending_operator_questions():
    """Return pending operator questions from the handoff.

    When all signed/build/audit/design queues are empty, the next action should
    not fall through to generic research if the handoff already records concrete
    operator questions. Those are authority-bearing design forks, so they route
    to Matt before any new concept/contract work.
    """
    handoff = read_file("MMI_THREAD_HANDOFF.md") or ""
    if "## Open Questions Still Pending" not in handoff:
        return []
    section = handoff.split("## Open Questions Still Pending", 1)[1]
    section = section.split("\n---", 1)[0]
    questions = []
    for line in section.splitlines():
        if not line.startswith("| OQ-"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) >= 2:
            questions.append(f"{parts[0]}: {parts[1]}")
    return questions

def check_drift():
    verifier = os.path.join(REPO, "scripts/verify_build_truth.py")
    if not os.path.exists(verifier):
        return False
    result = subprocess.run(
        [sys.executable, verifier],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    return "DRIFT" in result.stdout and result.returncode != 0

drifted = check_drift()
awaiting = get_awaiting_audit()
unbuilt = get_signed_unbuilt()
concept = get_next_concept_without_contract()
pending_questions = get_pending_operator_questions()

print("=" * 60)
if drifted:
    print("STOP: DRIFT DETECTED")
    print("ASSIGNED_TO: Matt")
    print("NEXT_PROMPT_GOES_TO: Matt - fix drift before anything else")
    print("OPERATOR_ACTION_REQUIRED: YES")
    print("IF YES: Run verify_build_truth.py and fix flagged items")
elif awaiting:
    # A build is implemented + tested but not yet gated. Route it to the Grok
    # completion gate before starting any new build. The exact command is
    # emitted so the audit step is not tribal memory.
    name = awaiting[0]
    slug = audit_task_slug(name)
    manifest_rel = f"audit_outputs/pending/{slug}.manifest.json"
    manifest_ok = os.path.exists(os.path.join(REPO, manifest_rel))
    print("MODE: AUDIT")
    print(f"AUTHORIZED_TASK: Run Grok completion gate for {name}")
    print("ASSIGNED_TO: Grok (negative-feedback auditor)")
    print("NEXT_PROMPT_GOES_TO: Cursor stages the build, runs the gate, then commits")
    print("OPERATOR_ACTION_REQUIRED: NO  (Grok activation is standing; no per-run permission)")
    print(
        f"RUN: python3 audit_tools/complete_gate.py --pre-commit "
        f'--task {slug} --claim "{name} build implemented + tested; ready for audit"'
    )
    print(
        f"MANIFEST: {manifest_rel} "
        f"({'present' if manifest_ok else 'MISSING - create before gate'})"
    )
    print("BLOCKED_UNTIL: complete_gate.py reports blocking=0 (0/0) AND build committed")
    print("NEXT_GATE: flip scoreboard row AWAITING_AUDIT -> GATED after clean audit + commit")
elif unbuilt:
    print("MODE: BUILD")
    print(f"AUTHORIZED_TASK: Build {unbuilt[0]}")
    print("ASSIGNED_TO: Cursor")
    print("NEXT_PROMPT_GOES_TO: Cursor")
    print("BLOCKED_UNTIL: NONE")
    print("OPERATOR_ACTION_REQUIRED: NO")
    print("NEXT_GATE: gate 0/0 + health score 85+ + hash reported")
elif concept:
    name = concept.replace("_Concept_Doc.md", "").replace("_", " ")
    print("MODE: DESIGN")
    print(f"AUTHORIZED_TASK: Draft contract for {name}")
    print("ASSIGNED_TO: Claude")
    print("NEXT_PROMPT_GOES_TO: Claude")
    print("BLOCKED_UNTIL: Matt signs section 11")
    print("OPERATOR_ACTION_REQUIRED: NO")
    print("NEXT_GATE: section 11 signed + build authorized")
elif pending_questions:
    print("MODE: OPERATOR_LOCK")
    print("AUTHORIZED_TASK: Resolve pending operator questions before next contract")
    print("ASSIGNED_TO: Matt")
    print("NEXT_PROMPT_GOES_TO: Matt")
    print("BLOCKED_UNTIL: OQ-4/OQ-5 answered or explicitly deferred")
    print("OPERATOR_ACTION_REQUIRED: YES")
    print("QUESTIONS: " + " | ".join(pending_questions))
    print("NEXT_GATE: answers recorded, then Claude drafts the next signed contract")
else:
    print("MODE: RESEARCH")
    print("AUTHORIZED_TASK: Research next phase requirements")
    print("ASSIGNED_TO: ChatGPT")
    print("NEXT_PROMPT_GOES_TO: ChatGPT")
    print("BLOCKED_UNTIL: Research returned and Claude drafts concept doc")
    print("OPERATOR_ACTION_REQUIRED: NO")
    print("NEXT_GATE: Concept doc committed")
print("=" * 60)
