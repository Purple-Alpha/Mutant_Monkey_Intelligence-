#!/usr/bin/env python3
import os
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
unbuilt = get_signed_unbuilt()
concept = get_next_concept_without_contract()

print("=" * 60)
if drifted:
    print("STOP: DRIFT DETECTED")
    print("ASSIGNED_TO: Matt")
    print("NEXT_PROMPT_GOES_TO: Matt - fix drift before anything else")
    print("OPERATOR_ACTION_REQUIRED: YES")
    print("IF YES: Run verify_build_truth.py and fix flagged items")
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
else:
    print("MODE: RESEARCH")
    print("AUTHORIZED_TASK: Research next phase requirements")
    print("ASSIGNED_TO: ChatGPT")
    print("NEXT_PROMPT_GOES_TO: ChatGPT")
    print("BLOCKED_UNTIL: Research returned and Claude drafts concept doc")
    print("OPERATOR_ACTION_REQUIRED: NO")
    print("NEXT_GATE: Concept doc committed")
print("=" * 60)
