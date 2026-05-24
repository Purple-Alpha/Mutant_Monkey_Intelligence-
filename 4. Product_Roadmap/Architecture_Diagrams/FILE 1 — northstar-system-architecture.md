# NorthStar System Architecture Diagram

Product Roadmap — Architecture Layer

## Purpose

High‑level architecture showing how NorthStar’s components interact:

- Delivery Engine

- Reporting Engine

- Training Engine

- SwarmCommand Engine (future)

- Client environment

## Diagram (Mermaid)

```
flowchart LR  
    ClientEmail\[Client Email Environment\] --\>|Simulation Delivery| DeliveryEngine  
    DeliveryEngine --\>|Click Data| TrainingEngine  
    DeliveryEngine --\>|Simulation Results| ReportingEngine  
    TrainingEngine --\>|Completion Data| ReportingEngine  
    ReportingEngine --\>|Monthly Reports| ClientLeadership  
  
    subgraph SwarmCommandEngine\[SwarmCommand Engine (Future)\]  
        DetectionAgents --\> ScoringAgents  
        ScoringAgents --\> WorkflowAgents  
        WorkflowAgents --\> DraftingAgents  
        DraftingAgents --\> ReportingEngine  
    end  
  
    DeliveryEngine --\> SwarmCommandEngine  
    SwarmCommandEngine --\> DeliveryEngine
```

