# MMI Host Evidence Bundle - Grading Tool Lockout

## Identity

- evidence_bundle_id: `MMI_HOST_EVIDENCE_BUNDLE_GRADING_TOOL_LOCKOUT_2026-07`
- produced_by: `Codex`
- produced_for: tool-restricted Gemini / external audit consumers
- authority_class: `HOST_ATTESTED_EVIDENCE_ONLY`
- build_authorization: `NOT_AUTHORIZED`
- review_artifact_acceptance_status: `INDEPENDENT_REVIEW_REQUIRED`

## Purpose

This bundle addresses reviewer environments where shell, git, or hash tools are unavailable.

It does not prove correctness, safety, build readiness, runtime behavior, or closure. It provides host-captured evidence that a tool-restricted reviewer may cite as `HOST_ATTESTED` instead of hallucinating shell, git, or SHA-256 operations.

## Host State

Command:

```text
git status --branch --short
```

Output:

```text
## mmi-phase2-commit...origin/mmi-phase2-commit
 M mmi/project_brain/status/LLM_LANE_LAWS_INDEX_2026-07.md
 M mmi/project_brain/status/LLM_MODEL_AUDIT_STANDARD_2026-07.md
?? mmi/project_brain/status/MMI_INDEPENDENT_GRADING_LAW_AUDIT_4918d4d_2026-07.md
```

## Commit Context

Command:

```text
git log --oneline -3
```

Output:

```text
4918d4d Add teaching marks to grading standard
f8b4934 Patch independent grading enforcement gaps
83dcb24 Codify high-intensity XML prompt law
```

Command:

```text
git rev-parse HEAD
```

Output:

```text
4918d4d2541a6d78c9eda2d738eabf2ebe6b8a46
```

## Hash Evidence

Command:

```text
sha256sum mmi/project_brain/status/LLM_MODEL_AUDIT_STANDARD_2026-07.md mmi/project_brain/status/LLM_LANE_LAWS_INDEX_2026-07.md mmi/project_brain/status/MMI_INDEPENDENT_GRADING_LAW_AUDIT_4918d4d_2026-07.md mmi/project_brain/status/MMI_GRADING_STRIKE_LEDGER.json
```

Output:

```text
ed74ee77bb9b0c3bd46821abf0aab6c41b5df7e3eba1af1dfdd0ef1fa4fc5ef8  mmi/project_brain/status/LLM_MODEL_AUDIT_STANDARD_2026-07.md
8c5c443ad32db845ec1d71856635e392a839c2c250047a470e9eb22a7de8b1f0  mmi/project_brain/status/LLM_LANE_LAWS_INDEX_2026-07.md
b233fc89fd2f1f383c342c0609b73e2496e576ddb5fdabca3734910bbb1c1e6e  mmi/project_brain/status/MMI_INDEPENDENT_GRADING_LAW_AUDIT_4918d4d_2026-07.md
9f47df626c936e0eb48f2718ff35ee6c699973574c3508476d251e9f251983ef  mmi/project_brain/status/MMI_GRADING_STRIKE_LEDGER.json
```

## Consumer Rules

- This bundle is `HOST_ATTESTED_UNSEALED`.
- It is fallback evidence for tool-restricted reviewers, not a full substitute for direct tool recomputation.
- It cannot by itself fully close critical hash-binding, evidence-discipline, or producer/grader identity criteria.
- Tool-restricted reviewers must mark hash verification mode as `HOST_ATTESTED`, not `TOOL_RECOMPUTED`.
- Tool-restricted reviewers must not claim they ran `git`, `sha256sum`, or shell commands.
- If this bundle is missing required artifact paths or hashes, the reviewer must mark verification as `NOT_VERIFIED`.
- If the workspace changes after this bundle, these hashes are stale and must not be reused as current-state evidence.

## Boundaries

- proves: host captured git status, recent commit context, HEAD hash, and SHA-256 outputs for the listed files at bundle creation time.
- does_not_prove: system safety, runtime behavior, implementation correctness, independent acceptance, or readiness to build.
- cannot_infer: permission to build, deploy, cleanup, reset, force-push, or close residual risks.
