# Sandbox Swarm Loop
Red and Blue Training Pit

## Purpose
The sandbox loop is where the swarm learns to stay ahead of new threats without risking production tenants.

## Inputs
- Anonymized weakness reports from production
- New threat intelligence
- Historical patterns from vector memory
- Synthetic scenarios

## Loop

```text
while True:
    # 1. Monitor
    pull weakness reports from production
    pull new threat intel
    pull historical patterns from vector memory

    # 2. Analyze
    Red agents generate synthetic attacks using:
        - new intel
        - production weaknesses
        - mutation strategies

    Blue agents attempt detection

    # 3. Plan
    if Blue fails:
        mutation engine clones Blue agent
        applies prompt, threshold, or heuristic mutation
        schedules A/B testing

    # 4. Execute
    run Red attack against Blue detection
    auditor produces verdict
    evaluate mutant vs baseline

    # 5. Knowledge Update
    if mutant > baseline:
        promote mutant to sandbox baseline
        generate defensive policy update
        send update to Production Policy Queue
```

## Safety Rules
- Sandbox may use Red agents.
- Sandbox may mutate Blue agents.
- Sandbox must not access raw production tenant data.
- Sandbox outputs defensive policy updates only.

## Outputs
- Synthetic attack cases
- Blue detection results
- Mutant evaluation reports
- Defensive policy updates
- Promotion recommendations
