# Data Flow Architecture

Product Roadmap — Architecture Layer

## Purpose

Show how data moves through the system from simulation → training → reporting.

## Diagram (Mermaid)

```
flowchart LR  
    Simulation\[Phishing Simulation\] --\> Clicks\[Click Data\]  
    Clicks --\> Training\[Micro‑Training Engine\]  
    Training --\> Completion\[Training Completion Data\]  
    Clicks --\> Scoring\[Risk Scoring Engine\]  
    Completion --\> Scoring  
    Scoring --\> Reporting\[Reporting Engine\]  
    Reporting --\> Leadership\[Leadership Output\]
```

