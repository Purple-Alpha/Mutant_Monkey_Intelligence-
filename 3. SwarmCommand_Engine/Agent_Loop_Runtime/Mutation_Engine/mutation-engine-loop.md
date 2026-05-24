# Mutation Engine Loop
Sandbox-Only Evolution Chamber

## Purpose
The mutation engine improves defensive agents in the sandbox by testing controlled variants against synthetic attacks and known weaknesses.

## Core Rule
Mutation is never allowed in production.

## Loop

```text
if detection_failed:
    clone = create_clone(BlueAgent)
    mutate(clone)
    run A/B test:
        clone vs baseline
    if clone_performs_better:
        promote clone
        write new rules to policy_update_queue
    else:
        retire clone
```

## Allowed Mutations
- Stricter validation
- New defensive heuristics
- New scoring weights
- New pattern embeddings
- New feature extraction rules
- Threshold adjustments
- Prompt refinements for defensive analysis

## Disallowed Mutations
- No personality changes
- No role changes
- No offensive capabilities
- No direct production deployment
- No bypassing audit

## Promotion Requirements
A mutant may only be promoted if:
- It beats the baseline on approved evaluation metrics.
- It does not increase false positives beyond policy limits.
- It passes auditor review.
- It produces a signed defensive policy update.
- It is approved for production policy queue review.

## Retirement Rules
Retire a mutant if:
- It underperforms baseline.
- It violates schema.
- It produces unapproved prose.
- It attempts scope expansion.
- It fails audit.
