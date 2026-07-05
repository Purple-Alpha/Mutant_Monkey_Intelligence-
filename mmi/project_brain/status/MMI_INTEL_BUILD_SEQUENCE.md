# MMI Intel Build Sequence

Date: 2026-06-29  
Authority: Matt (Super)

---

## Sequence (locked)

| Seed | Task id | Owner | Output | Gate |
|------|---------|-------|--------|------|
| **#3 (now)** | `mmi-security-intel-evaluator-pass` | Gemini Paid API | `lanes/RESEARCH_EVALUATOR_PASS_2026-06.md` | Crucible PDF/page-check |
| **#1 (after PASS)** | `mmi-intel-brief-template` | Claude | `intel/templates/INTEL_BRIEF_TEMPLATE.md` | Requires Evaluator PASS |

---

## Rigor authority

All research/audit prompts must include: `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md`

---

## Git note (2026-06-29)

MMI Phase 2 committed on branch **`mmi-phase2-commit`** (`b65abe2`) — orphan root commit due to corrupt objects on legacy `main`. Working tree unchanged. Optional: `git checkout main` then `git reset --hard mmi-phase2-commit` after backup if Matt wants `main` on clean history.

---

## Evaluator prompt

Use Template C in `MMI_RESEARCH_RIGOR_PROTOCOL.md`.
