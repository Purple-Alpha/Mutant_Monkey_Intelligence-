# NorthStar Inbox Shield

LangGraph proof of concept for the AI Phishing Essentials inbox analyst.

This is the business-facing runnable version. It uses xAI Grok through
`langchain-xai`, validates the model output with Pydantic, and returns the
same JSON shape needed for customer-facing reports and later SwarmCommand
producer-agent integration.

## Run

From a fresh PowerShell window where `XAI_API_KEY` is available:

```powershell
cd "C:\Unified Folder Structure NorthStar + SwarmCommand Venture\AI_Phishing_Simulation_Business\Inbox_Shield"
python inbox_shield_langgraph.py
```

The default run analyzes a built-in CEO wire-fraud sample.

To analyze your own email:

```powershell
python inbox_shield_langgraph.py path\to\email.txt
```

## Batch Testing

Put `.txt` or `.eml` samples in the `samples` folder, then run:

```powershell
python run_against_folder.py samples
```

Outputs:

```text
outputs/inbox_shield_results.csv
outputs/inbox_shield_results.jsonl
```

Use the CSV for quick sorting by `risk_score`, `recommended_action`, and
`impersonation_likelihood`. Use the JSONL when you need the full structured
verdict for each email.

## Mini Eval

Define expected outcomes per sample in `samples/expected_results.csv`:

```text
sample,risk_min,allowed_actions,is_fraud
ceo_wire_fraud.txt,80,block,true
legit_meeting_update.txt,0,safe,false
```

Run the analyzer, then the checker:

```powershell
python run_against_folder.py samples
python check_eval.py
```

The checker prints a per-sample PASS/FAIL table plus a summary including false
positives and missed fraud, and exits non-zero if any expectation is unmet so it
can be wired into CI later.

## Action Item Rule

`action_items` are defender actions for the recipient. They must not repeat the
attacker's requested task as if the user should comply. For a blocked wire-fraud
email, the model should recommend actions like "do not process the wire" and
"verify through a known phone number."

## Domain Legitimacy Rule

The model must not claim that a sender domain matches or does not match the real
organization unless the legitimate domain is present in the email or provided as
context. If the real domain is unknown, the correct wording is that domain
legitimacy cannot be confirmed from the email content.

## Known Warning

Current LangGraph may print a `LangChainPendingDeprecationWarning` about
`allowed_objects` during import. It is package-level noise and does not affect
the analysis result or output files.

## Current Model

Default:

```text
grok-4.3
```

Override for a single run:

```powershell
$env:INBOX_SHIELD_MODEL="grok-4.20-0309-non-reasoning"
python inbox_shield_langgraph.py
```

## Workflow

1. `analyze` - calls Grok with the NorthStar Inbox Shield prompt.
2. `validate` - parses and validates the JSON output against the schema.
3. `retry` - sends schema errors back to the model up to two times.
4. `give_up` - returns a conservative `needs_review` JSON fallback if the
   model still fails validation.

## Promotion Path

This script is not the final production path. The next version should be
wrapped as a sandbox-only SwarmCommand producer agent (`llm_detection_001`) in:

```text
C:\Unified Folder Structure NorthStar + SwarmCommand Venture\3. SwarmCommand_Engine\Agent_Loop_Runtime
```

That promotion path keeps the LLM behind audit, policy promotion, Guardrail 11,
the regression detector, and rollback machinery.
