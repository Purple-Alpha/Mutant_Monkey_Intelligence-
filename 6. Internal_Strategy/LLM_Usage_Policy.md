# NorthStar LLM Usage Policy (v1.0)

## 1. Purpose

This policy defines how Large Language Models (LLMs) may be used within the NorthStar Security program to ensure safe, compliant, and defensively oriented outcomes.

## 2. Allowed Use Cases

LLMs may be used for:

- Fraud-pattern and phishing-pattern analysis
- Defensive scenario design and abuse-case modeling
- Risk modeling and threat-surface mapping
- Email-fraud and invoice-authenticity evaluation
- Multi-agent safety and governance design
- Documentation, reporting, and summarization
- Synthetic dataset design and generation
- Code review for defensive logic (validation, sanitization, detection, logging)

## 3. Prohibited Use Cases

LLMs must **not** be used for:

- Generating real-world attack payloads, exploits, or malware
- Producing step-by-step system-compromise instructions
- Interacting with or targeting real infrastructure, networks, or production systems
- Testing against production systems or live customer environments
- Handling real customer data, PII, or regulated financial data
- Generating phishing or fraud content intended for real recipients
- Circumventing security controls or governance processes

## 4. Data Handling Requirements

- All examples must be **synthetic, anonymized, or fictional**.
- Do not include real customer names, email addresses, invoice numbers, domains, or identifiers.
- Do not paste secrets, credentials, API keys, or internal tokens into LLMs.
- Treat all LLM interactions as potentially observable by third parties.

## 5. Prompting Requirements

- All LLM sessions used for NorthStar work **must** begin with the **NorthStar Defensive Security System Prompt** (see `LLM_System_Prompt_Template.md`).
- Maintain a clearly **defensive** framing: detection, mitigation, monitoring, resilience, governance.
- Use "test scenario", "evaluation case", or "abuse case" language for harmful behaviors.
- Avoid aggressive or sensational phrasing (e.g., "how do I hack X"); reframe as defensive analysis.
- Avoid real-world system references; keep all examples on synthetic infrastructure.

## 6. Multi-Agent and AI-Security Requirements

When discussing multi-agent systems, swarms, or red-team-like components:

- Treat all such agents as **evaluation components** operating in sandboxed, controlled environments.
- Do not describe agents as autonomous in real-world environments.
- Focus on safety, governance, access control, logging, and adversarial evaluation that improves robustness.

## 7. Privacy, Compliance, and Logging

- Assume all real-world data must be protected and minimized.
- Prefer synthetic or anonymized data in all examples and prompts.
- Sensitive LLM-assisted design decisions (e.g., security architecture, governance changes) should be summarized in internal docs or tickets for auditability.
- LLMs must not be used as a storage system for sensitive or regulated data.

## 8. Review and Approval

- All LLM-generated code or configurations that touch security, fraud detection, or governance must be reviewed by a human engineer before merging.
- Any suspected misuse of LLMs must be reported to the project lead.
- This policy will be reviewed periodically as NorthStar and LLM capabilities evolve.

## 9. Violations

- Any violation of this policy must be reported to the project lead.
- LLM access may be restricted, revoked, or scoped down if misuse is detected.
- Repeat or material violations are tracked in the internal audit trail and may trigger a broader review of the policy itself, the tooling guardrails (see `LLM_Workflow_Integration_Plan.md`), and the system prompt.

## 10. Tooling Enforcement Reference

Engineering controls that operationalize this policy (pre-commit hooks, CI checks, `--llm-safe` mode, onboarding) are tracked separately in `LLM_Workflow_Integration_Plan.md`. Until those controls are implemented, all enforcement is procedural and runs through this policy + the system prompt template.

## Last Updated

2026-05-20
