# Trigger Routing Table Per Tier

**Status:** Spec-first routing table.
**Purpose:** Define which triggers wake which agents for Essentials, Plus, and Enterprise slices.
**Safety rule:** Routing can start defensive analysis, training, audit, and reporting work. Production-impacting actions remain approval-gated.

## 1. Trigger Families

| Trigger | Meaning |
|---|---|
| `DATA_INGESTED` | New raw event received |
| `EVENT_NORMALIZED` | Normalized event ready |
| `FEATURES_READY` | Feature payload ready |
| `EMBEDDING_READY` | Embedding stored |
| `WINDOW_CLOSED` | Hour/day/week window closed |
| `TREND_UPDATED` | New trend signal computed |
| `ANOMALY_DETECTED` | Anomaly score exceeds threshold |
| `DRIFT_DETECTED` | Drift threshold exceeded |
| `RISK_SPIKE` | Risk crosses configured boundary |
| `POLICY_CHANGED` | RBAC, policy, or tier config changed |
| `MODEL_UPDATED` | Model or scoring config changed |
| `SANDBOX_WEAKNESS_SPIKE` | Red battery or sandbox weakness exceeds threshold |
| `REGRESSION_ALERT_EMITTED` | Regression alert record appears |
| `PROJECT_DRIFT_DETECTED` | Docs/code/test baseline contradiction detected |

## 2. Essentials Routing

Essentials is stable, limited, and report-first.

```json
{
  "tier": "ESSENTIALS",
  "routes": {
    "DATA_INGESTED": ["Ingestion_Agent"],
    "EVENT_NORMALIZED": ["Feature_Engineering_Agent"],
    "FEATURES_READY": ["Embedding_Agent", "TimeSeries_Builder_Agent"],
    "WINDOW_CLOSED": ["MovingAverage_Agent", "Trend_Reporting_Agent"],
    "PROJECT_DRIFT_DETECTED": ["Swarm_Orchestrator_Agent"]
  }
}
```

Disabled by default:

- anomaly detection
- drift detection
- forecasting
- predictive modeling
- sandbox weakness auto-training

## 3. Plus Routing

Plus is the main product tier. It gets the full trend, anomaly, risk, and reporting path.

```json
{
  "tier": "PLUS",
  "routes": {
    "DATA_INGESTED": ["Ingestion_Agent", "Normalization_Agent"],
    "EVENT_NORMALIZED": ["Feature_Engineering_Agent"],
    "FEATURES_READY": ["Embedding_Agent", "TimeSeries_Builder_Agent"],
    "WINDOW_CLOSED": [
      "MovingAverage_Agent",
      "Decomposition_Agent",
      "ARIMA_Forecasting_Agent",
      "Anomaly_Detection_Agent"
    ],
    "TREND_UPDATED": ["Risk_Scoring_Agent"],
    "ANOMALY_DETECTED": ["Drift_Detection_Agent", "Predictive_Modeling_Agent"],
    "DRIFT_DETECTED": ["Predictive_Modeling_Agent"],
    "RISK_SPIKE": ["Risk_Scoring_Agent", "Trend_Reporting_Agent"],
    "SANDBOX_WEAKNESS_SPIKE": ["Swarm_Orchestrator_Agent"],
    "REGRESSION_ALERT_EMITTED": ["Swarm_Orchestrator_Agent"],
    "PROJECT_DRIFT_DETECTED": ["Swarm_Orchestrator_Agent"]
  }
}
```

Plus may start a one-hour defensive training loop for `SANDBOX_WEAKNESS_SPIKE` or `PROJECT_DRIFT_DETECTED`, but may not apply production changes without approval.

## 4. Enterprise Routing

Enterprise gets custom routing, full guardrail agents, tenant risk aggregation, and extended focus windows.

```json
{
  "tier": "ENTERPRISE",
  "routes": {
    "DATA_INGESTED": ["Ingestion_Agent", "Normalization_Agent", "Source_Classifier_Agent"],
    "EVENT_NORMALIZED": ["Feature_Engineering_Agent", "Integrity_Check_Agent"],
    "FEATURES_READY": ["Embedding_Agent", "Quality_Score_Agent", "TimeSeries_Builder_Agent"],
    "EMBEDDING_READY": ["Campaign_Clustering_Agent"],
    "WINDOW_CLOSED": [
      "MovingAverage_Agent",
      "Decomposition_Agent",
      "Seasonality_Agent",
      "Baseline_Model_Agent",
      "ARIMA_Forecasting_Agent",
      "Anomaly_Detection_Agent"
    ],
    "TREND_UPDATED": ["Risk_Scoring_Agent", "Tenant_Risk_Aggregator_Agent"],
    "ANOMALY_DETECTED": ["Drift_Detection_Agent", "Predictive_Modeling_Agent"],
    "DRIFT_DETECTED": ["Predictive_Modeling_Agent", "Drift_Guardrail_Agent"],
    "RISK_SPIKE": ["Trend_Reporting_Agent", "Tenant_Risk_Aggregator_Agent"],
    "POLICY_CHANGED": ["Swarm_Orchestrator_Agent", "RBAC_Enforcer_Agent"],
    "MODEL_UPDATED": ["Swarm_Orchestrator_Agent", "Execution_Contract_Agent"],
    "SANDBOX_WEAKNESS_SPIKE": ["Swarm_Orchestrator_Agent", "Execution_Contract_Agent"],
    "REGRESSION_ALERT_EMITTED": ["Swarm_Orchestrator_Agent", "RBAC_Enforcer_Agent"],
    "PROJECT_DRIFT_DETECTED": ["Swarm_Orchestrator_Agent", "Drift_Guardrail_Agent"]
  }
}
```

Enterprise routing is broader, but the same approval boundaries apply.

## 5. Trigger Event Shape

```json
{
  "trigger_id": "trigger_YYYYMMDD_HHMMSS",
  "trigger_type": "DATA_INGESTED",
  "source": "Ingestion_Agent",
  "tenant_id": "tenant_demo",
  "timestamp": "ISO-8601",
  "payload": {},
  "routing_hints": {
    "priority": "normal",
    "target_agents_override": null
  }
}
```

## 6. Routing Algorithm

1. Load trigger.
2. Load tenant slice descriptor.
3. Confirm trigger is enabled for tenant tier.
4. Load tier route.
5. Filter target agents by tenant-enabled agents.
6. Attach execution contract defaults.
7. Enforce RBAC and quota.
8. Dispatch or reject with audit event.

