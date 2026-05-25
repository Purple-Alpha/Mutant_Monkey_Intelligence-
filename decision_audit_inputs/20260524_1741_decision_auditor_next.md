# Decision Audit Packet - Decision Auditor next

## 1. Decision Under Review
Whether NorthStar should build the Independent Decision Auditor immediately after completing Tiered Detection Intensity, before starting another product-runtime detector or sales-facing feature.

## 2. Primary Recommendation
Build the Independent Decision Auditor next as local governance tooling under `audit_tools/decision_audit_runner.py`, with explicit Markdown decision packets under `decision_audit_inputs/`, local reports under `audit_outputs/decision_audits/`, and fail-closed verdict handling for `revise_before_proceeding`, `defer`, and `operator_decision_required`.

## 3. Rationale Given
Matt identified that the primary assistant's recommendations can steer build order, scope, and architecture before drift is visible. The project already uses spec-first lockdown and Grok code audits after implementation, but it does not yet have a second-model challenge before major direction-setting decisions. Building this lane now gives future choices a repeatable anti-drift check before more product runtime surfaces are added.

## 4. Rejected Alternatives
One alternative was to keep relying on the primary assistant's explanation and Matt's judgment only. That was rejected because it does not create an independent challenge layer. Another alternative was to build another detection capability first, such as additional email-authentication or metadata detectors. That was deferred because the existing runtime already has several detector surfaces, and the next strategic risk is decision drift rather than one missing detector. A third alternative was a larger multi-model panel. That was rejected for v1 because it adds cost and process weight before the simpler one-model lane is proven useful.

## 5. Current Project State
Tiered Detection Intensity is implemented, tested, and independently audited, with runtime baseline recorded as 658 passed and 1 skipped in `PROGRESS.md` and `PROJECT_HANDSHAKE.md`. The signed Decision Auditor spec is `4. Product_Roadmap/Independent_Decision_Auditor_Deep_Dive.md`; it locks the runner path, packet contract, verdict enum, fail-closed behavior, data-minimization boundary, and 20-test gate. Existing independent code-audit precedent lives in `audit_tools/grok_audit_runner.py`.

## 6. Constraints / Guardrails
The implementation must remain outside product runtime, must not import from or be imported by `core/`, must not write Blackboard, production state, operator state, Git, GitHub, or trackers automatically, and must not include secrets, raw client emails, raw financial strings, GitHub tokens, `.env` contents, or private audit outputs in decision packets. Matt keeps final authority over every verdict and must still explicitly issue `lock §11`, `start build`, commit, push, or override commands.

## 7. Operator Concern
Matt trusts the primary assistant but wants a second set of hands to challenge recommendations before the project commits to a direction.

## 8. What Would Change My Mind
If the auditor finds that this lane adds more bureaucracy than protection at the current stage, or that another runtime detector is clearly a higher-risk dependency for the next milestone, the build order should be revised or deferred.

## 9. Deadline / Urgency
Moderate urgency: the tool should be available before the next major build-lane selection or new subsystem spec lock.
