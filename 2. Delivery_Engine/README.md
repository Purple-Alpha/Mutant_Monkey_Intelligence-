# **2. Delivery_Engine**

How NorthStar actually delivers AI Phishing Essentials, month over month.

> **Layer:** NorthStar (commercial business — operational arm)
> **One‑thing filter:** Only add items here that move forward **one delivery workflow** end‑to‑end.

---

## **What Lives Here**

| Area | Purpose |
|---|---|
| **Phishing_Simulations** | Monthly simulation playbooks, send rules, safety guardrails |
| **Phishing_Simulations/Campaign_Examples** | Reference campaigns by industry (real estate, finance, healthcare, trades, legal) |
| **Training/Micro_Training_Scripts** | 2–4 minute training modules sent to employees who clicked |
| **Reporting** | Monthly Human‑Risk Report, Leadership Evidence Package, Incident‑Reporting Checklist |

---

## **End‑to‑End Delivery Workflow**

Mirrors §6 of the [Offer Sheet](../1.%20Business_Operations/AI_Phishing_Essentials_Offer_Sheet.md):

1. **Kickoff** — confirm scope, sign [`Authorization_Scope_Template`](../1.%20Business_Operations/Client_Documents/Authorization_Scope_Template.md), set blackout windows.
2. **Employee list import** — Canadian‑hosted, no credentials, deletable on request.
3. **Simulation** — one campaign/month, safe templates, no credential harvesting.
4. **Micro‑training** — auto‑sent only to clickers.
5. **Monthly report** — click rates, repeat‑clickers, department risk, recommendations.
6. **Leadership review** — Evidence Package delivered, renewal posture noted.

---

## **Current Assets**

- [ ] Phishing simulation playbook v1 (send rules, safety, exclusions).
- [ ] 3 starter campaign examples (one per priority industry).
- [ ] Micro‑training script v1 (post‑click 2–4 min module).
- [x] [`Reporting/# Monthly Human‑Risk Report.md`](./Reporting/%23%20Monthly%20Human%E2%80%91Risk%20Report.md) — monthly report template.
- [x] [`Reporting/Leadership_Summary.md`](./Reporting/Leadership_Summary.md) — leadership summary template.
- [x] [`Reporting/Leadership_Evidence_Package.md`](./Reporting/Leadership_Evidence_Package.md) — leadership evidence package.
- [x] [`Reporting/Internal_Report_Notes.md`](./Reporting/Internal_Report_Notes.md) — internal reporting notes.
- [x] [`Reporting/NorthStar_Security_Report_Template.md`](./Reporting/NorthStar_Security_Report_Template.md) — NorthStar report cover/template file.

---

## **Hard Guardrails**

These are non‑negotiable and mirror the signed Authorization & Scope:

- **No** credential harvesting.
- **No** malware, payloads, attachments, exploits, or ransomware simulations.
- **No** sensitive lures (HR complaints, layoffs, medical, harassment, disciplinary).
- **No** shaming or public reporting of individual results.
- **No** simulations on statutory holidays or known operationally sensitive periods.
- **All** client data stored in Canada; deleted on request.

---

## **See Also**

- [`../1. Business_Operations/AI_Phishing_Essentials_Offer_Sheet.md`](../1.%20Business_Operations/AI_Phishing_Essentials_Offer_Sheet.md) — the offer this engine delivers.
- [`../3. SwarmCommand_Engine`](../3.%20SwarmCommand_Engine) — automation that powers each step of this workflow.
- [`../5. Clients`](../5.%20Clients) — per‑client instance of this workflow.
