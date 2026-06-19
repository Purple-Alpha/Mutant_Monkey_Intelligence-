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
    "Gap5_Tenant_Baseline_Ingestion_Concept_Doc.md": [
        "Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md",
    ],
}

# Governance utility specs are tracked for build discipline, but they are not
# product concept lanes that should automatically route to Claude for a design
# contract.
CONCEPT_ROUTING_EXCLUSIONS = {
    "Project_Drift_Detector_Concept_Doc.md",
}

def read_file(path):
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        return None
    with open(full, encoding="utf-8") as f:
        return f.read()


STATE_FILE = "MMI_CURRENT_STATE.md"
PIN_RE = re.compile(r"\s*PIN\s*:\s*(on|true|yes)\s*$", re.IGNORECASE)


def _read_routing_block():
    """Return the routing block of the state file as a list of raw lines.

    The routing block is everything above the first blank line. The sections
    below the blank line (LAST_COMPLETED, queue notes, parked drafts) are
    human-authored context and are never parsed for routing.
    """

    content = read_file(STATE_FILE) or ""
    block = []
    for raw_line in content.splitlines():
        if not raw_line.strip():
            break
        block.append(raw_line)
    return block


def _block_to_pairs(block):
    pairs = []
    for raw_line in block:
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        pairs.append((key.strip(), value.strip()))
    return pairs


def get_manual_pin():
    """Honor an explicit operator pin in MMI_CURRENT_STATE.md.

    When the routing block contains a ``PIN: ON`` (or true/yes) line, the
    hand-written block is authoritative and the derived route is suppressed.
    This is the manual escape hatch for when Matt wants to freeze the
    dispatcher on a specific instruction. Without a PIN the dispatcher derives
    its route from the scoreboard automatically, so completed work is reflected
    the moment the scoreboard row changes — no hand-editing of this file.
    """

    block = _read_routing_block()
    if not any(PIN_RE.match(line) for line in block):
        return None
    pairs = [(k, v) for k, v in _block_to_pairs(block) if k.upper() != "PIN"]
    return pairs or None


def sync_state_file(lines):
    """Rewrite the routing block of the state file from the derived route.

    Everything from the first blank line down (the human-authored notes) is
    preserved verbatim. Returns True if the file content actually changed.
    """

    path = os.path.join(REPO, STATE_FILE)
    new_block = "\n".join(f"{key}: {value}" for key, value in lines)
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.read()
    boundary = existing.find("\n\n")
    tail = existing[boundary:] if boundary != -1 else "\n"
    new_content = new_block + tail
    if new_content == existing:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def routing_block_is_stale(lines):
    """True when the state file's routing block disagrees with the derived route."""

    current = _block_to_pairs(_read_routing_block())
    return current != [(key, value) for key, value in lines]


def is_git_tracked(path):
    """True only when a repo-relative path is already committed/tracked.

    Parallel sessions may leave roadmap drafts on disk. Those files are visible
    to drift detection, but they are not routing-authoritative until git tracks
    them.
    """

    result = subprocess.run(
        ["git", "-C", REPO, "ls-files", "--error-unmatch", path],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


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
    concepts = [
        f for f in os.listdir(roadmap)
        if "Concept_Doc" in f and is_git_tracked(os.path.join("4. Product_Roadmap", f))
    ]
    contracts = [
        f for f in os.listdir(roadmap)
        if "Contract" in f and is_git_tracked(os.path.join("4. Product_Roadmap", f))
    ]
    for concept in sorted(concepts):
        if concept in CONCEPT_ROUTING_EXCLUSIONS:
            continue
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

def _scoreboard_row_status(row_id):
    scoreboard = read_file("agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md") or ""
    prefix = f"| {row_id} |"
    for line in scoreboard.splitlines():
        if not line.startswith(prefix):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) >= 3:
            return parts[2].strip("`")
    return ""

def _all_rows_gated(row_ids):
    return all(_scoreboard_row_status(row_id).startswith("GATED") for row_id in row_ids)

def _operator_decisions_locked():
    state = read_file("MMI_CURRENT_STATE.md") or ""
    return (
        "OQ-4: Homeostasis remains inside Mode Controller" in state
        and "OQ-5: Tenant baseline ingestion does not require operator approval for every closed threat event" in state
    )

def get_collective_immune_design_task():
    """Depth-gate follow-on once control-plane prerequisites are done.

    The CIS path is the first organism gap after Mode Controller, Privacy
    Filter, and Safe-Stop are gated and OQ-4/OQ-5 are locked. At that point the
    research lane is no longer the next blocker; the design lane should draft
    the next CIS artifact.
    """
    if _all_rows_gated(("92", "93", "94")) and _operator_decisions_locked():
        return "Draft Collective Immune System concept doc / design contract"
    return None

def get_cortex_immune_interface_design_task():
    """Next organism gap after CIS is gated.

    ORGANISM_DOCTRINE_GAP_LIST.md lists Gap 3 as the next dependency after CIS
    and Safe-Stop: the cross-organ interface contract. When CIS row #95 is
    gated, generic research is no longer the actionable next state.
    """
    if (
        _scoreboard_row_status("95").startswith("GATED")
        and not is_contract_signed("Cortex_Immune_Interface_Design_Contract.md")
    ):
        return "Draft Cortex / Immune Interface concept doc / contract"
    return None

MC_ADVERSARIAL_CONTRACT = "Mode_Controller_Adversarial_Test_Suite_Contract.md"


def _contract_path(filename: str) -> str:
    return os.path.join(REPO, "4. Product_Roadmap", filename)


def get_independent_review_pending_task():
    """Return the first gated adversarial suite still waiting on review.

    GATED adversarial suites can still withhold the parent component's
    ADVERSARIALLY HARDENED claim until the review lane has checked the evidence.
    That is actionable MMI state and must not fall through to generic research.
    """
    scoreboard = read_file("agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md") or ""
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 7:
            continue
        row_id, name = parts[0], parts[1]
        runtime_status = parts[2].strip("`")
        blockers = parts[6]
        if (
            runtime_status.startswith("GATED")
            and "Adversarial Test Suite" in name
            and (
                "Independent review pending" in blockers
                or "review pending" in blockers
            )
        ):
            parent = blockers.split(" before ", 1)[1] if " before " in blockers else blockers
            return row_id, name, parent
    return None


def get_mode_controller_adversarial_sign_task():
    """Mode Controller adversarial suite drafted but not yet §11 signed."""
    if not _scoreboard_row_status("98").startswith("GATED"):
        return None
    if not os.path.exists(_contract_path(MC_ADVERSARIAL_CONTRACT)):
        return None
    if is_contract_signed(MC_ADVERSARIAL_CONTRACT):
        return None
    return MC_ADVERSARIAL_CONTRACT


def get_mode_controller_adversarial_task():
    """Next retroactive adversarial suite after Privacy Filter is hardened."""
    if not _scoreboard_row_status("98").startswith("GATED"):
        return None
    if is_contract_signed(MC_ADVERSARIAL_CONTRACT):
        return None
    if os.path.exists(_contract_path(MC_ADVERSARIAL_CONTRACT)):
        return None  # draft exists — route to Matt signature, not Gemini
    return (
        "Send Mode Controller signed contract to Gemini with the adversarial "
        "attack prompt"
    )

def get_next_research_task():
    """Explicit research target after the current gated organism work.

    Gap 4 (Homeostasis Engine Policy) is deferred by OQ-4: Homeostasis remains
    inside Mode Controller this phase. The next active dependency is Gap 5,
    which needs dual-model research before Claude drafts a concept/contract.
    """
    if _scoreboard_row_status("96").startswith("GATED") and not is_contract_signed(
        "Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md"
    ):
        return (
            "Research Gap 5 — Memory Consolidation / Tenant Baseline Ingestion: "
            "evidence-to-baseline promotion rules, required evidence fields, "
            "operator-approval thresholds, rollback/reversibility, and audit schema"
        )
    if (
        _scoreboard_row_status("98").startswith("GATED")
        and not os.path.exists(_contract_path(MC_ADVERSARIAL_CONTRACT))
    ):
        return (
            "Send Mode Controller signed contract to Gemini with the adversarial "
            "attack prompt"
        )
    return "Research next phase requirements"

LANE_ESCALATION_DEFAULT = (
    "only on authority/scope/live-data/material-risk fork"
)
REVIEW_ESCALATION = (
    "only if Codex flags authority, scope, live-data, material-risk, or hardening-claim decision"
)


def _contract_display_name(filename):
    """Human label from a roadmap contract filename."""
    base = filename.replace(".md", "")
    for suffix in (
        "_Adversarial_Test_Suite_Contract",
        "_Design_Contract",
        "_Contract_v2",
        "_Contract",
    ):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return base.replace("_", " ").strip()


def iter_signed_contract_files():
    """Yield signed §11 contract filenames under 4. Product_Roadmap/."""
    roadmap = os.path.join(REPO, "4. Product_Roadmap")
    if not os.path.exists(roadmap):
        return
    for filename in sorted(os.listdir(roadmap)):
        if "Contract" not in filename or not filename.endswith(".md"):
            continue
        if is_contract_signed(filename):
            yield filename


def _contract_scoreboard_build_state(contract_file, scoreboard_text):
    """Classify how a signed contract relates to the scoreboard build lifecycle."""
    for line in scoreboard_text.splitlines():
        if not line.startswith("|"):
            continue
        if contract_file not in line:
            continue
        if "SIGNED_UNBUILT" in line:
            return "scoreboard_unbuilt"
        if "AWAITING_AUDIT" in line or "GATED" in line:
            return "built_or_in_progress"
    return "off_scoreboard"


# Northstar signed builds that lack a scoreboard lifecycle row (drift).
# Completed v2 rows (#103/#104) removed — gated 2026-06-18.
HANDOFF_WAITING_BUILD_CONTRACTS: dict[str, str] = {}

# Signed contracts in external repos/lanes (not Northstar scoreboard rows).
EXTERNAL_LANE_CONTRACTS: dict[str, tuple[str, str]] = {
    "Threat Intelligence Daemon": (
        "Threat_Intelligence_Daemon_Design_Contract.md",
        "/home/socialarchitect/mutant_monkey_intel/",
    ),
}

# Evidence-based delegation scores (higher = delegate first).
DELEGATION_SCORES: dict[str, int] = {
    "SCOREBOARD_READY": 100,
    "NEEDS_SCOREBOARD_ROW": 88,
    "INTAKE_CLASSIFY_BATCH": 72,
    "EXTERNAL_LANE": 68,
    "NEEDS_MMI_REVIEW": 65,
    "RESEARCH": 58,
    "PARKED_DRAFT": 25,
}

EXTERNAL_LANE_STATUS_FILE = "mmi/EXTERNAL_LANE_STATUS.md"


def get_completed_external_lanes():
    """External lanes marked COMPLETE in the status registry."""
    content = read_file(EXTERNAL_LANE_STATUS_FILE) or ""
    completed = []
    for line in content.splitlines():
        if line.startswith("- ") and "COMPLETE" in line:
            name = line[2:].split(":", 1)[0].strip()
            if name:
                completed.append(name)
    return completed


def is_external_lane_complete(display_name: str) -> bool:
    return display_name in get_completed_external_lanes()


WORKER_COMPLETION_UPDATE = (
    "MMI first after any worker completion: append evidence to the relevant MMI "
    "record (intake/gate/decision log as applicable), update MMI_CURRENT_STATE.md "
    "LAST_COMPLETED prose, run python3 scripts/mmi_dispatch.py --sync, commit "
    "routing-authority files, then python3 scripts/mmi_dispatch.py --verify"
)


def get_off_scoreboard_signed_contracts():
    """Handoff-recorded signed Northstar builds that lack a scoreboard lifecycle row."""
    scoreboard = read_file("agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md") or ""
    drift = []
    for display_name, contract_file in HANDOFF_WAITING_BUILD_CONTRACTS.items():
        if not is_contract_signed(contract_file):
            continue
        if _contract_scoreboard_build_state(contract_file, scoreboard) == "off_scoreboard":
            drift.append((display_name, contract_file))
    return drift


def get_parked_untracked_roadmap_drafts():
    """Untracked roadmap files visible in git status (PARKED_DRAFT)."""
    result = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain", "4. Product_Roadmap"],
        capture_output=True,
        text=True,
        check=False,
    )
    drafts = []
    for line in result.stdout.splitlines():
        if not line.startswith("??"):
            continue
        path = line[3:].strip().strip('"')
        drafts.append(os.path.basename(path))
    return sorted(drafts)


def get_intake_classified_parked_drafts():
    """Filenames listed under '## Classified files' in the intake registry."""
    content = read_file("mmi/PARKED_DRAFT_CLASSIFICATIONS.md") or ""
    if "## Classified files" not in content:
        return []
    section = content.split("## Classified files", 1)[1]
    section = section.split("\n---", 1)[0]
    classified = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and stripped.endswith(".md"):
            classified.append(stripped[2:].strip())
    return sorted(classified)


def get_unclassified_parked_drafts():
    """Parked drafts still needing batch intake classification."""
    parked = get_parked_untracked_roadmap_drafts()
    classified = set(get_intake_classified_parked_drafts())
    return [name for name in parked if name not in classified]


def get_parked_untracked_concept_drafts():
    """Untracked concept docs visible in git status (subset of parked drafts)."""
    return [d for d in get_parked_untracked_roadmap_drafts() if "Concept_Doc" in d]


def _delegation_task(
    *,
    phase,
    name,
    classification,
    source_evidence,
    why,
    assigned_worker,
    matt_action_required=False,
    extra=None,
):
    """Structured delegation task with evidence-based score."""
    score = DELEGATION_SCORES.get(classification, 0)
    return {
        "phase": phase,
        "name": name,
        "classification": classification,
        "score": score,
        "source_evidence": source_evidence,
        "why": why,
        "assigned_worker": assigned_worker,
        "matt_action_required": matt_action_required,
        "extra": extra or {},
    }


def collect_delegation_tasks():
    """Evidence-backed tasks MMI may delegate (sorted by score descending)."""
    tasks = []

    for name in get_signed_unbuilt():
        tasks.append(_delegation_task(
            phase="BUILD",
            name=name,
            classification="SCOREBOARD_READY",
            source_evidence="agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md SIGNED_UNBUILT row",
            why="Signed scoreboard row is build-ready; highest-priority mechanical lane",
            assigned_worker="Cursor → Codex → Cursor",
        ))

    for display_name, contract_file in get_off_scoreboard_signed_contracts():
        tasks.append(_delegation_task(
            phase="BUILD",
            name=f"Add scoreboard SIGNED_UNBUILT row for {display_name}",
            classification="NEEDS_SCOREBOARD_ROW",
            source_evidence=f"4. Product_Roadmap/{contract_file} signed; no lifecycle row",
            why="Signed Northstar contract without scoreboard row blocks BUILD routing",
            assigned_worker="Cursor",
        ))

    parked = get_unclassified_parked_drafts()
    if parked:
        file_list = ", ".join(parked)
        tasks.append(_delegation_task(
            phase="INTAKE",
            name=f"Classify parked roadmap drafts ({len(parked)} files)",
            classification="INTAKE_CLASSIFY_BATCH",
            source_evidence=f"git status untracked: {file_list}",
            why=(
                "Untracked parallel-session drafts need MMI intake classification "
                "before any promotion; batch review is the actionable unblock"
            ),
            assigned_worker="Cursor",
            extra={"files": parked},
        ))

    for display_name, (contract_file, build_root) in EXTERNAL_LANE_CONTRACTS.items():
        if not is_contract_signed(contract_file):
            continue
        if is_external_lane_complete(display_name):
            continue
        tasks.append(_delegation_task(
            phase="EXTERNAL",
            name=f"Build {display_name} (external lane)",
            classification="EXTERNAL_LANE",
            source_evidence=(
                f"4. Product_Roadmap/{contract_file} §11 signed; "
                f"external root {build_root}"
            ),
            why=(
                "Contract is signed and scoped to an external repo lane — "
                "not a Northstar scoreboard row; delegate build to external surface"
            ),
            assigned_worker="Cursor",
            extra={"build_root": build_root, "contract_file": contract_file},
        ))

    concept = get_next_concept_without_contract()
    if concept:
        label = concept.replace("_Concept_Doc.md", "").replace("_", " ")
        tasks.append(_delegation_task(
            phase="DESIGN",
            name=f"Draft contract for {label}",
            classification="NEEDS_MMI_REVIEW",
            source_evidence=f"4. Product_Roadmap/{concept} tracked without contract",
            why="Tracked concept doc lacks a matching signed contract",
            assigned_worker="Claude",
        ))

    for task_name, phase in (
        (get_collective_immune_design_task(), "DESIGN"),
        (get_cortex_immune_interface_design_task(), "DESIGN"),
    ):
        if task_name:
            tasks.append(_delegation_task(
                phase=phase,
                name=task_name,
                classification="NEEDS_MMI_REVIEW",
                source_evidence="organism gap design lane (scoreboard + OQ state)",
                why="Prerequisite control-plane rows gated; next organism design artifact",
                assigned_worker="Claude",
            ))

    research_task = get_next_research_task()
    if research_task != "Research next phase requirements":
        worker = (
            "Gemini"
            if research_task.startswith("Send Mode Controller signed contract to Gemini")
            else "ChatGPT → Gemini"
        )
        tasks.append(_delegation_task(
            phase="RESEARCH",
            name=research_task,
            classification="RESEARCH",
            source_evidence="get_next_research_task()",
            why="Specific research target surfaced from gated organism state",
            assigned_worker=worker,
        ))

    for draft in get_unclassified_parked_drafts():
        if any(draft in (t.get("extra", {}).get("files") or []) for t in tasks
               if t["classification"] == "INTAKE_CLASSIFY_BATCH"):
            continue
        tasks.append(_delegation_task(
            phase="CONCEPT",
            name=draft,
            classification="PARKED_DRAFT",
            source_evidence=f"git status untracked 4. Product_Roadmap/{draft}",
            why="Single parked draft — lower priority than batch intake classification",
            assigned_worker="Cursor",
        ))

    tasks.sort(key=lambda t: (-t["score"], t["name"]))
    return tasks


def _format_candidate_from_task(task):
    """Legacy single-line candidate entry (compass / audit trail)."""
    parts = [
        f"[{task['phase']}] {task['name']}",
        f"Classification: {task['classification']}",
        f"Score: {task['score']}",
        f"Source: {task['source_evidence']}",
        f"Worker: {task['assigned_worker']}",
    ]
    if task["matt_action_required"]:
        parts.append("Matt action: YES")
    else:
        parts.append("Matt action: NO")
    return " | ".join(parts)


def collect_all_clear_candidates():
    """Delegated-task compass (backward-compatible name)."""
    return [_format_candidate_from_task(t) for t in collect_delegation_tasks()]


def _scoreboard_queue_counts():
    """Compact scoreboard lifecycle counts for CURRENT_PROJECT_TRUTH."""
    scoreboard = read_file("agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md") or ""
    counts = {"SIGNED_UNBUILT": 0, "AWAITING_AUDIT": 0, "GATED": 0}
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        status = parts[2].strip("`")
        for key in counts:
            if status.startswith(key):
                counts[key] += 1
                break
    return counts


def _derive_current_project_truth():
    counts = _scoreboard_queue_counts()
    parked = len(get_parked_untracked_roadmap_drafts())
    return (
        f"Northstar control-plane queue: {counts['SIGNED_UNBUILT']} SIGNED_UNBUILT, "
        f"{counts['AWAITING_AUDIT']} AWAITING_AUDIT, {counts['GATED']} GATED rows; "
        f"{parked} untracked roadmap draft(s) in git status"
    )


def _format_task_scoreboard(tasks):
    if not tasks:
        return "(no evidence-backed tasks surfaced)"
    return " || ".join(
        f"{t['name']} [{t['classification']} score={t['score']}]"
        for t in tasks
    )


def _format_lower_alternatives(tasks, top):
    alts = [t for t in tasks if t is not top][:5]
    if not alts:
        return "(none)"
    return " || ".join(f"{t['name']} (score={t['score']})" for t in alts)


def _build_delegation_lines(derived):
    """Delegate the highest-scored evidence-backed task (project-brain mode)."""
    tasks = collect_delegation_tasks()
    truth = _derive_current_project_truth()

    if not tasks:
        lines = [
            ("MODE", "ALL_CLEAR"),
            ("AUTHORIZED_TASK", "No evidence-backed next task surfaced from repo state"),
            ("CURRENT_PROJECT_TRUTH", truth),
            ("TASK_SCOREBOARD", "(empty)"),
        ]
        lines = _append_lane_doctrine(
            lines,
            build_authorization_implied="NO",
        )
        lines += [
            ("ASSIGNED_TO", "Matt"),
            ("NEXT_PROMPT_GOES_TO", "Matt"),
            ("REQUIRED_UPDATE_AFTER_COMPLETION", WORKER_COMPLETION_UPDATE),
            ("OPERATOR_ACTION_REQUIRED", "YES — no delegable task from current evidence"),
            ("CANDIDATES_NOT_AUTHORIZATION", "YES — queue empty; Matt supplies next evidence"),
            ("CANDIDATES", "(none — external lanes complete, no scoreboard BUILD/AUDIT queue)"),
            ("NEXT_GATE", "new signed contract, scoreboard row, or intake evidence"),
        ]
        return derived, lines

    top = tasks[0]
    lines = [
        ("MODE", "DELEGATE"),
        ("AUTHORIZED_TASK", top["name"]),
        ("CURRENT_PROJECT_TRUTH", truth),
        ("TASK_SCOREBOARD", _format_task_scoreboard(tasks)),
        ("NEXT_DELEGATED_TASK", top["name"]),
        ("ASSIGNED_WORKER", top["assigned_worker"]),
        ("ASSIGNED_TO", top["assigned_worker"]),
        ("WHY_THIS_TASK", top["why"]),
        ("TASK_SCORE", str(top["score"])),
        ("LOWER_SCORE_ALTERNATIVES", _format_lower_alternatives(tasks, top)),
        ("SOURCE_EVIDENCE", top["source_evidence"]),
        ("REQUIRED_UPDATE_AFTER_COMPLETION", WORKER_COMPLETION_UPDATE),
    ]
    lines = _append_lane_doctrine(
        lines,
        build_authorization_implied=(
            "YES — delegated from repo evidence"
            if top["classification"] in ("SCOREBOARD_READY", "EXTERNAL_LANE")
            else "NO — delegated intake/design/research lane"
        ),
    )
    op_required = (
        "YES — authority/scope/signature fork"
        if top["matt_action_required"]
        else "NO"
    )
    lines += [
        ("NEXT_PROMPT_GOES_TO", top["assigned_worker"]),
        ("BLOCKED_UNTIL", f"{top['assigned_worker']} completes delegated task and MMI update"),
        ("OPERATOR_ACTION_REQUIRED", op_required),
        ("CANDIDATES_NOT_AUTHORIZATION", (
            "YES — lower-scored alternatives are context only; delegation is evidence-based"
        )),
        ("CANDIDATES", " || ".join(collect_all_clear_candidates())),
        ("NEXT_GATE", "worker completion → MMI update first → --verify PASS"),
    ]
    if top["classification"] == "SCOREBOARD_READY":
        lines.insert(6, ("PRE_BUILD_REVIEW", "Codex"))
    return derived, lines


def _build_all_clear_lines(derived):
    """Backward-compatible entry: delegates when evidence exists."""
    return _build_delegation_lines(derived)


def _lane_doctrine_fields(
    *,
    operator_names_target="Matt",
    mmi_assigns_lane="YES",
    lane_escalation=LANE_ESCALATION_DEFAULT,
    build_authorization_implied=None,
):
    """Standard Matt-target / MMI-lane output labels (Decision 2)."""
    fields = [
        ("OPERATOR_NAMES_TARGET", operator_names_target),
        ("MMI_ASSIGNS_LANE", mmi_assigns_lane),
        ("LANE_ESCALATION_TO_MATT", lane_escalation),
    ]
    if build_authorization_implied is not None:
        fields.append(("BUILD_AUTHORIZATION_IMPLIED", build_authorization_implied))
    return fields


def _append_lane_doctrine(lines, **kwargs):
    """Insert lane-doctrine fields after AUTHORIZED_TASK when present."""
    doctrine = _lane_doctrine_fields(**kwargs)
    insert_at = 1
    for idx, (key, _) in enumerate(lines):
        if key == "AUTHORIZED_TASK":
            insert_at = idx + 1
            break
    return lines[:insert_at] + doctrine + lines[insert_at:]


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

ROUTING_AUTHORITY_FILES = (
    "MMI_CURRENT_STATE.md",
    "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
    "scripts/mmi_dispatch.py",
)

DRIFT_SUMMARY_RE = re.compile(
    r"SUMMARY:\s*(\d+)\s*BLOCK,\s*(\d+)\s*BLOCK-candidate,\s*(\d+)\s*WARN"
)


def _run_script(relpath):
    """Run a repo script with the repo interpreter; return CompletedProcess or None."""
    path = os.path.join(REPO, relpath)
    if not os.path.exists(path):
        return None
    return subprocess.run(
        [sys.executable, path],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )


def _uncommitted_routing_files():
    """Routing-authority files with uncommitted changes (work not yet recorded)."""
    result = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    dirty = []
    for line in result.stdout.splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip().strip('"')
        if path in ROUTING_AUTHORITY_FILES:
            dirty.append(path)
    return dirty


def _pairs_from_route(lines):
    return dict(lines)


def _synthetic_build_route():
    """BUILD route shape for doctrine verification (no scoreboard mutation)."""
    lines = [
        ("MODE", "BUILD"),
        ("AUTHORIZED_TASK", "Build Example Component"),
        ("ASSIGNED_TO", "Cursor → Codex → Cursor"),
        ("PRE_BUILD_REVIEW", "Codex"),
        ("NEXT_PROMPT_GOES_TO", "Cursor (draft plan) → Codex (review) → Cursor (build)"),
        ("BLOCKED_UNTIL", "Codex clears build plan"),
        ("OPERATOR_ACTION_REQUIRED", "NO"),
    ]
    return _append_lane_doctrine(
        lines,
        build_authorization_implied="YES — §11 signed on scoreboard SIGNED_UNBUILT row",
    )


def _synthetic_review_route():
    """REVIEW route shape for doctrine verification."""
    lines = [
        ("MODE", "REVIEW"),
        ("AUTHORIZED_TASK", "Independent review Example #0"),
        ("ASSIGNED_TO", "Codex"),
        ("NEXT_PROMPT_GOES_TO", "Codex"),
        ("OPERATOR_ACTION_REQUIRED", "NO"),
        ("BLOCKED_UNTIL", "Codex review returns findings or clearance"),
    ]
    return _append_lane_doctrine(
        lines,
        lane_escalation=REVIEW_ESCALATION,
        build_authorization_implied="NO",
    )


def run_doctrine_checks():
    """Routing-doctrine compliance checks (Decision 5)."""
    checks = []
    routing_rules = read_file("mmi/MMI_ROUTING_RULES.md") or ""
    authority = read_file("mmi/MMI_AUTHORITY_MATRIX.md") or ""
    protocol = read_file("mmi/MMI_PROTOCOL.md") or ""

    checks.append((
        "Codex" in routing_rules and "assigns the lane" in routing_rules,
        "Codex and lane doctrine in mmi/MMI_ROUTING_RULES.md",
    ))
    checks.append((
        "Codex" in authority and "Pre-build plan review" in authority,
        "Codex and pre-build review in mmi/MMI_AUTHORITY_MATRIX.md",
    ))
    checks.append((
        "MMI delegates" in protocol and "assigns the lane" in protocol,
        "Matt-target / MMI-lane split in mmi/MMI_PROTOCOL.md",
    ))

    _, delegate_lines = _build_delegation_lines("doctrine-check")
    delegate = _pairs_from_route(delegate_lines)
    checks.append((
        delegate.get("MODE") in ("DELEGATE", "ALL_CLEAR")
        and "TASK_SCOREBOARD" in delegate
        and (
            "NEXT_DELEGATED_TASK" in delegate
            or delegate.get("MODE") == "ALL_CLEAR"
        )
        and "CANDIDATES_NOT_AUTHORIZATION" in delegate,
        "DELEGATE emits scored taskboard with NOT_AUTHORIZATION guard",
    ))

    off_board = get_off_scoreboard_signed_contracts()
    if off_board:
        scoreboard_text = delegate.get("TASK_SCOREBOARD", "")
        checks.append((
            "NEEDS_SCOREBOARD_ROW" in scoreboard_text,
            "off-scoreboard signed contracts labeled NEEDS_SCOREBOARD_ROW",
        ))
    else:
        checks.append((True, "off-scoreboard signed contract labeling (no drift contracts surfaced)"))

    tasks = collect_delegation_tasks()
    if tasks:
        checks.append((
            tasks[0]["score"] >= (tasks[1]["score"] if len(tasks) > 1 else 0),
            "delegation tasks sorted by score descending",
        ))
    else:
        checks.append((True, "delegation task scoring (no tasks in this snapshot)"))

    build_pairs = _pairs_from_route(_synthetic_build_route())
    checks.append((
        build_pairs.get("PRE_BUILD_REVIEW") == "Codex"
        and "Codex" in build_pairs.get("ASSIGNED_TO", ""),
        "BUILD route models Cursor → Codex pre-build → Cursor",
    ))

    review_pairs = _pairs_from_route(_synthetic_review_route())
    checks.append((
        review_pairs.get("ASSIGNED_TO") == "Codex"
        and review_pairs.get("OPERATOR_ACTION_REQUIRED") == "NO",
        "REVIEW route assigns Codex with OPERATOR_ACTION_REQUIRED: NO",
    ))

    checks.append((
        delegate.get("MMI_ASSIGNS_LANE") == "YES"
        and delegate.get("OPERATOR_NAMES_TARGET") == "Matt",
        "DELEGATE includes OPERATOR_NAMES_TARGET / MMI_ASSIGNS_LANE labels",
    ))

    dispatch_src = read_file("scripts/mmi_dispatch.py") or ""
    checks.append((
        "def run_doctrine_checks" in dispatch_src
        and "collect_delegation_tasks" in dispatch_src
        and "PRE_BUILD_REVIEW" in dispatch_src,
        "dispatcher source includes doctrine verify and delegation scoring",
    ))

    return checks


def run_verify():
    """Confirm the current MMI state was done properly.

    This is the dispatcher's other half: it gives the next task, and --verify
    proves the work behind the current state is actually complete and
    consistent — routing block in sync, routing-authority files committed,
    build truth verified, and no drift BLOCKs — before anything advances.
    Returns 0 on PASS, 1 on FAIL.
    """
    _, lines = build_route_lines()
    pairs = dict(lines)
    print("=" * 60)
    print("MMI VERIFY — was the work done properly?")
    print(f"current task: MODE: {pairs.get('MODE', '')}")
    print(f"              {pairs.get('AUTHORIZED_TASK', '')}")
    print("-" * 60)

    checks = []

    stale = routing_block_is_stale(lines)
    checks.append((
        not stale,
        "MMI_CURRENT_STATE.md routing block in sync with derived state"
        + ("" if not stale else " — run: python3 scripts/mmi_dispatch.py --sync"),
    ))

    dirty = _uncommitted_routing_files()
    checks.append((
        not dirty,
        "routing-authority files committed"
        + ("" if not dirty else f" — uncommitted: {', '.join(dirty)}"),
    ))

    bt = _run_script("scripts/verify_build_truth.py")
    if bt is None:
        checks.append((False, "build-truth verifier present (scripts/verify_build_truth.py)"))
    else:
        ok = bt.returncode == 0 and "BUILD TRUTH VERIFIED" in bt.stdout
        checks.append((
            ok,
            "build truth verified (docs agree with code+git)"
            + ("" if ok else " — DRIFT; see verify_build_truth.py output"),
        ))

    dd = _run_script("scripts/detect_drift.py")
    if dd is None:
        checks.append((False, "drift detector present (scripts/detect_drift.py)"))
    else:
        match = DRIFT_SUMMARY_RE.search(dd.stdout)
        if not match:
            checks.append((False, "drift detector summary parseable"))
        else:
            nblock, ncand, nwarn = (int(match.group(i)) for i in (1, 2, 3))
            checks.append((
                nblock == 0,
                f"drift: {nblock} BLOCK, {ncand} BLOCK-candidate, {nwarn} WARN "
                "(BLOCK must be 0)",
            ))

    for ok, label in run_doctrine_checks():
        checks.append((ok, f"doctrine: {label}"))

    for ok, label in checks:
        print(f"[ {('ok' if ok else 'FAIL'):>4} ] {label}")
    print("-" * 60)
    passed = all(ok for ok, _ in checks)
    if passed:
        print("VERDICT: PASS — current state is properly done and consistent.")
    else:
        print("VERDICT: FAIL — resolve the FAIL line(s) above before advancing.")
    print("=" * 60)
    return 0 if passed else 1


def build_route_lines():
    """Derive the routing block from the scoreboard/contract graph.

    This is the single derived source of truth. Returns ``(source, lines)``
    where ``lines`` is an ordered list of ``(key, value)`` pairs. The state
    file is only a generated mirror of this (see ``sync_state_file``) plus an
    optional manual ``PIN`` (see ``get_manual_pin``). Because the route is
    recomputed on every run, completed work shows up the moment the scoreboard
    row changes — there is no separate state file to hand-edit.
    """

    if check_drift():
        return "drift", [
            ("STOP", "DRIFT DETECTED"),
            ("ASSIGNED_TO", "Matt"),
            ("NEXT_PROMPT_GOES_TO", "Matt - fix drift before anything else"),
            ("OPERATOR_ACTION_REQUIRED", "YES"),
            ("IF YES", "Run verify_build_truth.py and fix flagged items"),
        ]

    derived = "derived from scoreboard"

    awaiting = get_awaiting_audit()
    if awaiting:
        # A build is implemented + tested but not yet gated. Route it to the
        # Grok completion gate before starting any new build. The exact command
        # is emitted so the audit step is not tribal memory.
        name = awaiting[0]
        slug = audit_task_slug(name)
        manifest_rel = f"audit_outputs/pending/{slug}.manifest.json"
        manifest_ok = os.path.exists(os.path.join(REPO, manifest_rel))
        return derived, [
            ("MODE", "AUDIT"),
            ("AUTHORIZED_TASK", f"Run Grok completion gate for {name}"),
            ("ASSIGNED_TO", "Grok (negative-feedback auditor)"),
            ("NEXT_PROMPT_GOES_TO", "Cursor stages the build, runs the gate, then commits"),
            ("OPERATOR_ACTION_REQUIRED", "NO  (Grok activation is standing; no per-run permission)"),
            ("RUN", f'python3 audit_tools/complete_gate.py --pre-commit --task {slug} --claim "{name} build implemented + tested; ready for audit"'),
            ("MANIFEST", f"{manifest_rel} ({'present' if manifest_ok else 'MISSING - create before gate'})"),
            ("BLOCKED_UNTIL", "complete_gate.py reports blocking=0 (0/0) AND build committed"),
            ("NEXT_GATE", "flip scoreboard row AWAITING_AUDIT -> GATED after clean audit + commit"),
        ]

    unbuilt = get_signed_unbuilt()
    if unbuilt:
        lines = [
            ("MODE", "BUILD"),
            ("AUTHORIZED_TASK", f"Build {unbuilt[0]}"),
            ("ASSIGNED_TO", "Cursor → Codex → Cursor"),
            ("PRE_BUILD_REVIEW", "Codex"),
            ("NEXT_PROMPT_GOES_TO", "Cursor (draft plan) → Codex (review) → Cursor (build)"),
            ("BLOCKED_UNTIL", "Codex clears build plan; then implementation + tests complete"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "Codex review → Cursor build → gate 0/0 + health score 85+ + hash reported"),
        ]
        lines = _append_lane_doctrine(
            lines,
            build_authorization_implied="YES — §11 signed on scoreboard SIGNED_UNBUILT row",
        )
        return derived, lines

    mode_controller_adversarial_sign = get_mode_controller_adversarial_sign_task()
    if mode_controller_adversarial_sign:
        label = mode_controller_adversarial_sign.replace('_', ' ').replace('.md', '')
        return derived, [
            ("MODE", "AWAITING §11 SIGNATURE"),
            ("AUTHORIZED_TASK", f"Sign {label}"),
            ("ASSIGNED_TO", "Matt"),
            ("NEXT_PROMPT_GOES_TO", "Cursor (after §11 signed)"),
            ("BLOCKED_UNTIL", "Matt signs §11"),
            ("OPERATOR_ACTION_REQUIRED", "YES — §11 signature required"),
            ("NEXT_GATE", "§11 signed → Cursor implements Mode Controller adversarial test families"),
        ]

    mode_controller_adversarial_task = get_mode_controller_adversarial_task()
    if mode_controller_adversarial_task:
        return derived, [
            ("MODE", "RESEARCH"),
            ("AUTHORIZED_TASK", mode_controller_adversarial_task),
            ("ASSIGNED_TO", "Gemini"),
            ("NEXT_PROMPT_GOES_TO", "Gemini"),
            ("BLOCKED_UNTIL", "Gemini returns Mode Controller adversarial red-team output; Claude drafts the adversarial suite contract"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "Gemini red-team packet returned, then Claude drafts Mode Controller adversarial test suite contract for Matt signature"),
        ]

    independent_review_task = get_independent_review_pending_task()
    if independent_review_task:
        row_id, name, parent = independent_review_task
        lines = [
            ("MODE", "REVIEW"),
            ("AUTHORIZED_TASK", f"Independent review {name} #{row_id}"),
            ("ASSIGNED_TO", "Codex"),
            ("NEXT_PROMPT_GOES_TO", "Codex"),
            ("BLOCKED_UNTIL", f"Codex review returns findings or clearance before {parent}"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("HARDENING_CLAIM", "Matt only — Codex may recommend; may not grant ADVERSARIALLY HARDENED"),
            ("NEXT_GATE", "review result recorded; Matt grants hardened claim if review clears it"),
        ]
        lines = _append_lane_doctrine(
            lines,
            lane_escalation=REVIEW_ESCALATION,
            build_authorization_implied="NO",
        )
        return derived, lines

    concept = get_next_concept_without_contract()
    if concept:
        name = concept.replace("_Concept_Doc.md", "").replace("_", " ")
        return derived, [
            ("MODE", "DESIGN"),
            ("AUTHORIZED_TASK", f"Draft contract for {name}"),
            ("ASSIGNED_TO", "Claude"),
            ("NEXT_PROMPT_GOES_TO", "Claude"),
            ("BLOCKED_UNTIL", "Matt signs section 11"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "section 11 signed + build authorized"),
        ]

    pending_questions = get_pending_operator_questions()
    if pending_questions:
        return derived, [
            ("MODE", "OPERATOR_LOCK"),
            ("AUTHORIZED_TASK", "Resolve pending operator questions before next contract"),
            ("ASSIGNED_TO", "Matt"),
            ("NEXT_PROMPT_GOES_TO", "Matt"),
            ("BLOCKED_UNTIL", "OQ-4/OQ-5 answered or explicitly deferred"),
            ("OPERATOR_ACTION_REQUIRED", "YES"),
            ("QUESTIONS", " | ".join(pending_questions)),
            ("NEXT_GATE", "answers recorded, then Claude drafts the next signed contract"),
        ]

    cis_design_task = get_collective_immune_design_task()
    if cis_design_task:
        return derived, [
            ("MODE", "DESIGN"),
            ("AUTHORIZED_TASK", cis_design_task),
            ("ASSIGNED_TO", "Claude"),
            ("NEXT_PROMPT_GOES_TO", "Claude"),
            ("BLOCKED_UNTIL", "Matt signs section 11 before any CIS build"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "concept/contract committed, then §11 signature before build"),
        ]

    cortex_immune_task = get_cortex_immune_interface_design_task()
    if cortex_immune_task:
        return derived, [
            ("MODE", "DESIGN"),
            ("AUTHORIZED_TASK", cortex_immune_task),
            ("ASSIGNED_TO", "Claude"),
            ("NEXT_PROMPT_GOES_TO", "Claude"),
            ("BLOCKED_UNTIL", "Matt signs section 11 before any interface build"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "concept/contract committed, then §11 signature before build"),
        ]

    research_task = get_next_research_task()
    if research_task == "Research next phase requirements":
        return _build_all_clear_lines(derived)
    lines = [("MODE", "RESEARCH"), ("AUTHORIZED_TASK", research_task)]
    if research_task.startswith("Send Mode Controller signed contract to Gemini"):
        lines += [
            ("ASSIGNED_TO", "Gemini"),
            ("NEXT_PROMPT_GOES_TO", "Gemini"),
            ("BLOCKED_UNTIL", "Gemini returns Mode Controller adversarial red-team output; Claude drafts the adversarial suite contract"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "Gemini red-team packet returned, then Claude drafts Mode Controller adversarial test suite contract for Matt signature"),
        ]
    else:
        lines += [
            ("ASSIGNED_TO", "ChatGPT"),
            ("NEXT_PROMPT_GOES_TO", "ChatGPT"),
            ("BLOCKED_UNTIL", "ChatGPT research + Gemini cross-check returned; Claude drafts concept doc"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "dual-model research packet committed, then concept doc committed"),
        ]
    return derived, lines


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if "--verify" in argv:
        return run_verify()

    do_sync = "--sync" in argv

    pin = get_manual_pin()
    if pin is not None:
        source, lines = "MMI_CURRENT_STATE.md (manual PIN)", pin
    else:
        source, lines = build_route_lines()

    print("=" * 60)
    for key, value in lines:
        print(f"{key}: {value}")
    print(f"SOURCE: {source}")
    print("=" * 60)

    if do_sync:
        if pin is not None:
            print("--sync skipped: MMI_CURRENT_STATE.md is PIN-locked (manual override).")
        else:
            changed = sync_state_file(lines)
            print(
                "--sync: MMI_CURRENT_STATE.md routing block "
                + ("updated to match derived state." if changed else "already current.")
            )
    elif pin is None and routing_block_is_stale(lines):
        print(
            "NOTE: MMI_CURRENT_STATE.md routing block is stale vs derived state. "
            "Run: python3 scripts/mmi_dispatch.py --sync"
        )

    if not do_sync:
        print(
            "DONE_CHECK: confirm the work behind this state was done properly → "
            "python3 scripts/mmi_dispatch.py --verify"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
