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
        return derived, [
            ("MODE", "BUILD"),
            ("AUTHORIZED_TASK", f"Build {unbuilt[0]}"),
            ("ASSIGNED_TO", "Cursor"),
            ("NEXT_PROMPT_GOES_TO", "Cursor"),
            ("BLOCKED_UNTIL", "NONE"),
            ("OPERATOR_ACTION_REQUIRED", "NO"),
            ("NEXT_GATE", "gate 0/0 + health score 85+ + hash reported"),
        ]

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
        return derived, [
            ("MODE", "REVIEW"),
            ("AUTHORIZED_TASK", f"Independent review {name} #{row_id}"),
            ("ASSIGNED_TO", "Matt / independent reviewer"),
            ("NEXT_PROMPT_GOES_TO", "Matt"),
            ("BLOCKED_UNTIL", f"review returns findings/clearance before {parent}"),
            ("OPERATOR_ACTION_REQUIRED", "YES — choose reviewer or accept/return the evidence"),
            ("NEXT_GATE", "review result recorded; only then update the parent hardened claim if review clears it"),
        ]

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
        # Genuine all-clear: no awaiting-audit, unbuilt, sign, review, concept,
        # operator-question, or design work is queued. This is an explicit
        # terminal state, not the old misleading generic-RESEARCH fallback.
        return derived, [
            ("MODE", "ALL_CLEAR"),
            ("AUTHORIZED_TASK", "All queued control-plane work is built, gated, and hardened — no pending build/audit/review/design item. Awaiting Matt's next-phase authorization."),
            ("ASSIGNED_TO", "Matt"),
            ("NEXT_PROMPT_GOES_TO", "Matt"),
            ("BLOCKED_UNTIL", "Matt names the next phase target (build, research, or design)"),
            ("OPERATOR_ACTION_REQUIRED", "YES — choose the next MMI task"),
            ("NEXT_GATE", "next explicit Matt authorization"),
        ]
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
