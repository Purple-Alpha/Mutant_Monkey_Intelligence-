MODE: RESEARCH
AUTHORIZED_TASK: Research next phase requirements
ASSIGNED_TO: ChatGPT
NEXT_PROMPT_GOES_TO: ChatGPT
BLOCKED_UNTIL: Research returned and Claude drafts concept doc
OPERATOR_ACTION_REQUIRED: NO
NEXT_GATE: Concept doc committed
LAST_COMPLETED: Safe-Stop State Machine #94 + Amendment 01 — gated 0/0 — commit cf3f273

OPERATOR DECISIONS LOCKED:

OQ-4: Homeostasis remains inside Mode Controller. No separate Homeostasis Engine contract at this phase. Only create a separate contract if Homeostasis gains independent action authority.

OQ-5: Tenant baseline ingestion does not require operator approval for every closed threat event. Operator approval is required only when the closed event meets or exceeds the defined risk threshold below.

High-impact triggers requiring operator approval (any one is sufficient):
1. Verdict was high_risk or blocked_or_hold_recommended
2. Evidence would change a vendor payment baseline
3. Evidence would change a sender identity baseline
4. Evidence would change a geo/location baseline
5. Evidence would affect more than one tenant
6. Evidence came from a conflict resolved by Reconciliation
7. Evidence depends on fission, mutation, privacy-breaker, or safe-stop context

Below-threshold events may enter governed ingestion only if all pass: schema validation, provenance validation, tenant scope validation, reconciliation closure, audit logging, and rollback evidence.
