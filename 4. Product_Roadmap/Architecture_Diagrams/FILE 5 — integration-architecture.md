# Integration Architecture

Product Roadmap — Architecture Layer

## Purpose

Show how NorthStar integrates with client systems and external services.

## Diagram (Mermaid)

```
flowchart LR  
    ClientEmail\[Client Email System\] --\> DeliveryEngine\[NorthStar Delivery Engine\]  
    DeliveryEngine --\> ReportingEngine\[NorthStar Reporting Engine\]  
    ReportingEngine --\> ClientLeadership\[Client Leadership\]  
  
    DeliveryEngine --\> SwarmCommand\[SwarmCommand Engine (Future)\]  
    SwarmCommand --\> DeliveryEngine  
  
    SwarmCommand --\> ExternalThreatIntel\[External Threat Intelligence (Optional)\]
```


