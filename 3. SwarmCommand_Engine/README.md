# **3. SwarmCommand_Engine**

The internal automation engine that lets NorthStar deliver and operate like a much larger team.

> **Layer:** SwarmCommand (internal engine) → seedbed for the 60‑agent product.
> **One‑thing filter:** Only add agents/workflows here that **remove a step** from a real NorthStar delivery, outreach, or reporting motion — or that **de‑risk** a future platform capability.

---

## **What Lives Here**

| Area | Purpose |
|---|---|
| **Workflows** | End‑to‑end automated sequences (kickoff → simulation → report → renewal) |
| **Workflow_Agents** | Agents that orchestrate steps inside a workflow |
| **Drafting_Agents** (under `SwarmCommand_Engine/Agents/`) | Generate outreach, training scripts, reports, lures |
| **Scoring_Agents** | Score click data, repeat‑clicker risk, department risk |
| **Experiments** | Time‑boxed R&D not yet in production |
| **Experiments/Detection_Sandbox** | Test new detection / lure / scoring techniques safely |
| **Future_Platform_Agents** | Staging area for agents being promoted to the 60‑agent platform |
| **Agent_Loop_Runtime** | Unified Blackboard + MAPE-K + sandbox + governance loop for the future 60-agent runtime |

---

## **Operating Rules**

1. **Every agent must point at a real job.** No "interesting" agents without an owner workflow.
2. **Promotion path:** `Experiments` → `Workflow_Agents` / `Scoring_Agents` / `Drafting_Agents` → `Future_Platform_Agents` once productizable.
3. **Safety first.** No agent may bypass the Delivery_Engine hard guardrails (no credential harvesting, no malware, no sensitive lures, Canadian data only).
4. **One workflow, one file.** Workflows are documented as a single markdown file per workflow.

---

## **Current Priorities (in order)**

- [ ] **Drafting_Agent: Outreach Email** — generate cold email variants from the buyer profile.
- [ ] **Drafting_Agent: Phishing Lure** — generate safe, industry‑specific lures.
- [ ] **Workflow_Agent: Monthly Delivery** — orchestrates the 6‑step Delivery Workflow.
- [ ] **Scoring_Agent: Click Risk** — produces the Monthly Human‑Risk Report.
- [ ] **Drafting_Agent: Monthly Report** — turns scoring output into client‑ready prose.
- [ ] **Agent_Loop_Runtime: Blackboard Models** — define the shared memory schema all future agents will write to.

Anything beyond these waits.

---

## **See Also**

- [`../2. Delivery_Engine`](../2.%20Delivery_Engine) — the workflows these agents automate.
- [`../4. Product_Roadmap`](../4.%20Product_Roadmap) — 60‑agent platform vision and architecture.
- [`../Unified Folder Structure - NorthStar + SwarmCommand Venture.md`](../Unified%20Folder%20Structure%20-%20NorthStar%20+%20SwarmCommand%20Venture.md) — venture operating doc.
