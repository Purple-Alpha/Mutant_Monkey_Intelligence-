# Inbox Shield Freelance Revenue Kit

Purpose: turn the working Inbox Shield demo into a 30-day cashflow asset without
inventing a new product or overpromising security outcomes.

## Proof Line

Use this as the top-level credibility line:

```text
Built a LangGraph + Grok 4.3 email-risk analyzer with Pydantic validation,
retry-on-bad-JSON, batch testing, CSV/JSONL outputs, and a labelled eval gate.
Current mini-eval: 5/5 passed, 0 false positives, 0 missed fraud.
```

Run the proof locally:

```powershell
cd "C:\Unified Folder Structure NorthStar + SwarmCommand Venture\AI_Phishing_Simulation_Business\Inbox_Shield"
.\run_demo.ps1
```

## Service Listing 1

### Title
LangGraph Workflow with Validated JSON Output

### Offer
I will build a small LangGraph workflow that turns messy inputs into validated,
structured JSON your app can trust.

### Best Fit
- Internal tools
- AI analysts
- Email / ticket / document triage
- Lightweight agent workflows
- Founder demos that need to stop returning unstructured model prose

### Deliverables
- LangGraph workflow with 2-4 nodes
- Pydantic output schema
- Retry-on-bad-output loop
- Conservative fallback path
- CLI runner
- README with exact run commands

### Starter Price
```text
$300-$800 fixed scope
```

## Service Listing 2

### Title
AI Evaluation Harness for Your Existing LLM App

### Offer
I will add a labelled PASS/FAIL eval harness to your existing AI workflow so you
can stop guessing whether prompt changes made the product better or worse.

### Best Fit
- Teams with a working prompt but no regression tests
- AI SaaS prototypes
- Security, compliance, support, or ops workflows
- Any app where false positives / false negatives matter

### Deliverables
- Labelled sample contract (`expected_results.csv` or JSONL)
- Batch runner
- PASS/FAIL comparator
- False-positive / missed-case summary
- Non-zero exit code for CI or local gates

### Starter Price
```text
$250-$700 fixed scope
```

## Service Listing 3

### Title
xAI Grok / Claude / OpenAI Integration Cleanup

### Offer
I will replace brittle one-off LLM calls with a safer integration layer:
environment keys, structured prompts, validated output, retries, and a clean
fallback.

### Best Fit
- Founders switching LLM providers
- Scripts that break when model output changes
- JSON extraction tools
- Prototype agents that need to become reliable enough for demos

### Deliverables
- Provider integration using existing API key
- Env-var based secret loading
- Structured system prompt
- Output validation
- Error handling
- Demo command

### Starter Price
```text
$200-$600 fixed scope
```

## Proposal Template - LangGraph / Agent Workflow

```text
Hey [Name],

I can help with this. I recently built a LangGraph workflow that analyzes inbound
emails with Grok 4.3, validates the model output with Pydantic, retries invalid
JSON, and runs a labelled eval gate. The current demo passes 5/5 labelled cases
with 0 false positives and 0 missed fraud.

For your project, I would keep the scope tight:
1. define the state schema and output contract,
2. build the graph nodes,
3. add validation + retry/fallback,
4. include a small batch/eval runner so you can test changes without guessing.

I can deliver a first working version in [X days] for [fixed price or hourly].
```

## Proposal Template - Eval Harness

```text
Hey [Name],

The risky part of this kind of AI workflow is not the first prompt working once;
it is knowing whether it still works after the next prompt/model change.

I can add a small eval harness around your existing workflow:
- labelled input samples,
- expected output contract,
- batch runner,
- PASS/FAIL report,
- false-positive and missed-case summary,
- non-zero exit code so it can later run in CI.

I built this pattern for an email-risk analyzer this week. It now prints a clean
5/5 passed report instead of relying on manual inspection.

If you can share 5-10 representative samples, I can turn this around quickly.
```

## Proposal Template - Provider Swap / Integration

```text
Hey [Name],

I can do the provider swap safely. I would avoid just replacing one import and
calling it done; the safer path is:
1. env-var based API key loading,
2. model initialization,
3. structured prompt,
4. output validation,
5. retry on invalid JSON,
6. conservative fallback,
7. a smoke test command so you know it works locally.

I just completed this for a Grok 4.3 + LangGraph workflow and can apply the same
pattern here.
```

## What Not To Promise

Do not promise:

- "Guaranteed phishing detection"
- "Replaces Microsoft Defender / Google security"
- "100% accurate"
- "Fully autonomous security analyst"
- "Production-ready SOC replacement"

Say instead:

- "Structured AI triage"
- "Human-review acceleration"
- "Eval-gated prototype"
- "Validated JSON outputs"
- "Small, testable workflow"

## 30-Day Execution Rule

No new product build is required for this revenue path.

The work is:

1. Submit 5 targeted proposals.
2. Use the proof line.
3. Offer one of the three scoped services.
4. Keep each first job under 10 hours.
5. Get one paid result, then decide what to improve.
