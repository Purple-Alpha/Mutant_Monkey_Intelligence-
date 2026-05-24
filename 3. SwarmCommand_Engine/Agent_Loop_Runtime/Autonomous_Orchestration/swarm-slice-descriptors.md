# Swarm Slice Descriptors

**Status:** Spec-first product packaging layer.
**Purpose:** Define how one physical swarm behaves like separate tenant-scoped swarms across Essentials, Plus, and Enterprise.

## 1. Core Idea

NorthStar can share physical agent capacity while presenting each tenant with a private logical swarm.

Every message, trigger, contract, and result carries `tenant_id`. The orchestrator loads that tenant's slice descriptor before dispatching work.

## 2. Essentials

```json
{
  "tier": "ESSENTIALS",
  "enabled_agents": [
    "Ingestion_Agent",
    "Normalization_Agent",
    "Feature_Engineering_Agent",
    "Embedding_Agent",
    "TimeSeries_Builder_Agent",
    "MovingAverage_Agent",
    "Trend_Reporting_Agent",
    "Swarm_Orchestrator_Agent"
  ],
  "enabled_triggers": [
    "DATA_INGESTED",
    "EVENT_NORMALIZED",
    "FEATURES_READY",
    "WINDOW_CLOSED",
    "PROJECT_DRIFT_DETECTED"
  ],
  "trigger_routing_overrides": {},
  "execution_contract_defaults": {
    "focus_window_ms": 900000,
    "allowed_drift": 0.10,
    "max_retries": 2,
    "fallback_agent": "Swarm_Orchestrator_Agent"
  },
  "resource_quota": {
    "max_events_per_day": 20000,
    "max_concurrent_tasks": 10
  }
}
```

Essentials is the stable entry tier: limited autonomy, basic trend reporting, no advanced anomaly or forecasting path.

## 3. Plus

```json
{
  "tier": "PLUS",
  "enabled_agents": [
    "Ingestion_Agent",
    "Normalization_Agent",
    "Source_Classifier_Agent",
    "Integrity_Check_Agent",
    "Feature_Engineering_Agent",
    "Embedding_Agent",
    "TimeSeries_Builder_Agent",
    "MovingAverage_Agent",
    "Decomposition_Agent",
    "ARIMA_Forecasting_Agent",
    "Anomaly_Detection_Agent",
    "Drift_Detection_Agent",
    "Predictive_Modeling_Agent",
    "Risk_Scoring_Agent",
    "User_Susceptibility_Agent",
    "Trend_Reporting_Agent",
    "Swarm_Orchestrator_Agent"
  ],
  "enabled_triggers": [
    "DATA_INGESTED",
    "EVENT_NORMALIZED",
    "FEATURES_READY",
    "WINDOW_CLOSED",
    "TREND_UPDATED",
    "ANOMALY_DETECTED",
    "DRIFT_DETECTED",
    "RISK_SPIKE",
    "SANDBOX_WEAKNESS_SPIKE",
    "REGRESSION_ALERT_EMITTED",
    "PROJECT_DRIFT_DETECTED"
  ],
  "trigger_routing_overrides": {},
  "execution_contract_defaults": {
    "focus_window_ms": 3600000,
    "allowed_drift": 0.15,
    "max_retries": 3,
    "fallback_agent": "Swarm_Orchestrator_Agent"
  },
  "resource_quota": {
    "max_events_per_day": 100000,
    "max_concurrent_tasks": 50
  }
}
```

Plus is the main product tier: full trend pipeline, anomaly detection, drift detection, risk scoring, and defensive training triggers.

## 4. Enterprise

```json
{
  "tier": "ENTERPRISE",
  "enabled_agents": [
    "Ingestion_Agent",
    "Normalization_Agent",
    "Source_Classifier_Agent",
    "Integrity_Check_Agent",
    "Feature_Engineering_Agent",
    "Embedding_Agent",
    "Quality_Score_Agent",
    "TimeSeries_Builder_Agent",
    "MovingAverage_Agent",
    "Decomposition_Agent",
    "Seasonality_Agent",
    "Baseline_Model_Agent",
    "ARIMA_Forecasting_Agent",
    "Campaign_Clustering_Agent",
    "Anomaly_Detection_Agent",
    "Drift_Detection_Agent",
    "Predictive_Modeling_Agent",
    "Risk_Scoring_Agent",
    "User_Susceptibility_Agent",
    "Tenant_Risk_Aggregator_Agent",
    "Trend_Reporting_Agent",
    "Trigger_Router_Agent",
    "Execution_Contract_Agent",
    "Drift_Guardrail_Agent",
    "RBAC_Enforcer_Agent",
    "Tenant_Isolation_Agent",
    "Swarm_Orchestrator_Agent"
  ],
  "enabled_triggers": [
    "DATA_INGESTED",
    "EVENT_NORMALIZED",
    "FEATURES_READY",
    "EMBEDDING_READY",
    "WINDOW_CLOSED",
    "TREND_UPDATED",
    "ANOMALY_DETECTED",
    "DRIFT_DETECTED",
    "RISK_SPIKE",
    "POLICY_CHANGED",
    "MODEL_UPDATED",
    "SANDBOX_WEAKNESS_SPIKE",
    "REGRESSION_ALERT_EMITTED",
    "PROJECT_DRIFT_DETECTED"
  ],
  "trigger_routing_overrides": {
    "DRIFT_DETECTED": ["Predictive_Modeling_Agent", "Tenant_Risk_Aggregator_Agent", "Drift_Guardrail_Agent"],
    "RISK_SPIKE": ["Trend_Reporting_Agent", "Tenant_Risk_Aggregator_Agent"]
  },
  "execution_contract_defaults": {
    "focus_window_ms": 7200000,
    "allowed_drift": 0.20,
    "max_retries": 5,
    "fallback_agent": "Swarm_Orchestrator_Agent"
  },
  "resource_quota": {
    "max_events_per_day": 500000,
    "max_concurrent_tasks": 200
  }
}
```

Enterprise unlocks custom routing, campaign intelligence, tenant-level aggregation, and the full guardrail/autonomy layer.

## 5. Runtime Rules

1. Load tenant slice before routing.
2. Disabled agents cannot receive work for that tenant.
3. Disabled triggers are ignored or logged as non-actionable.
4. Quotas apply before dispatch.
5. Trigger routing overrides may add or narrow agents, but may not bypass RBAC or production approval boundaries.

