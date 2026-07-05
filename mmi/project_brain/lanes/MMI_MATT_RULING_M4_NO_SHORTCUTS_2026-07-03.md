# Matt Ruling — M4 No Shortcuts / Full Matrix Bar

**Date:** 2026-07-03  
**Authority:** Matt (product owner)  
**Lane:** Decision record — binds spec r2.5+ and all agent lanes  
**Supersedes:** §13.1.6 Option 1 ("lesser `M4_MET` milestone") — **rejected**

---

## Ruling

MMI has **not** taken shortcuts on this project. We will **not** start now.

**PERFECT** in doctrine means the full matrix pass-line bundle for the 48h final — including replay-verified draft patches for every exploit tried (research §1.3 #7). That bar is not renamed, lowered, or split into a "good enough" finish line.

**`M4_MET` is the matrix-aligned terminal:** capture + sanitizer + inline attempt log + **replay-verified doctrine draft patch** for every TCB-attested exploit. Capture presence alone is **not** sufficient.

**`perfect_claim: false` remains pinned** in evidence until operator **GATED** attestation. Technical pass at ROLLUP ≠ promotional PERFECT claim. Honesty until victory.

**Surpassing the bar** is encouraged **after** the bar is real — stronger falsifiers, tighter chains, untrimmable attempt logs — never **instead of** the bar.

---

## Why

Shortcut culture produces checkbox security — the industry default MMI exists to reject. Un-fakeable metrics or nothing. If we accept capture-only evidence or lesser milestones in the spec, the same rationalization follows in the build and in what we tell ourselves.

The aspiration — disciplined proof first, then maybe the first real AGI-grade cyber defense stack — only remains plausible if the proof object stays militant.

---

## Spec binding (r2.5)

| Item | Value |
|------|-------|
| `M4_REPLAY_REMEDIATION_REQUIRED` | `true` |
| `draft_ok` | `complete(chain) ∧ replay_complete(chain)` |
| T15 | Replay failure → `M4_NOT_MET` |
| `perfect_gate_remaining` | `[]` iff `M4_MET`; else lists failed pass lines |
| Lesser milestone / Option 1 | **Removed** |

**Filed by:** Cursor per Matt instruction  
**Not claimed:** BUILDABLE, PERFECT achieved, M4 closed, GATED, build authorization
