# Agent Enablement Map Per Tier

**Status:** Spec-first product and RBAC matrix.
**Purpose:** Provide the clean tier matrix for the future 60-agent platform.

Legend:

- `Y` = enabled
- `N` = disabled

## 1. Ingestion and Normalization Cluster

| Agent | Count | Essentials | Plus | Enterprise |
|---|---:|:---:|:---:|:---:|
| `Ingestion_Agent` | 3 | Y | Y | Y |
| `Normalization_Agent` | 3 | Y | Y | Y |
| `Source_Classifier_Agent` | 2 | N | Y | Y |
| `Integrity_Check_Agent` | 2 | N | Y | Y |

## 2. Feature and Embedding Cluster

| Agent | Count | Essentials | Plus | Enterprise |
|---|---:|:---:|:---:|:---:|
| `Feature_Engineering_Agent` | 4 | Y | Y | Y |
| `Embedding_Agent` | 4 | Y | Y | Y |
| `Quality_Score_Agent` | 2 | N | N | Y |

## 3. Time-Series and Trend Cluster

| Agent | Count | Essentials | Plus | Enterprise |
|---|---:|:---:|:---:|:---:|
| `TimeSeries_Builder_Agent` | 3 | Y | Y | Y |
| `MovingAverage_Agent` | 2 | Y | Y | Y |
| `Decomposition_Agent` | 2 | N | Y | Y |
| `Seasonality_Agent` | 1 | N | N | Y |
| `Baseline_Model_Agent` | 2 | N | N | Y |

## 4. Anomaly, Drift, and Forecast Cluster

| Agent | Count | Essentials | Plus | Enterprise |
|---|---:|:---:|:---:|:---:|
| `Anomaly_Detection_Agent` | 3 | N | Y | Y |
| `Drift_Detection_Agent` | 3 | N | Y | Y |
| `ARIMA_Forecasting_Agent` | 2 | N | Y | Y |
| `Campaign_Clustering_Agent` | 2 | N | N | Y |

## 5. Risk, Scoring, and Reporting Cluster

| Agent | Count | Essentials | Plus | Enterprise |
|---|---:|:---:|:---:|:---:|
| `Risk_Scoring_Agent` | 4 | N | Y | Y |
| `User_Susceptibility_Agent` | 2 | N | Y | Y |
| `Tenant_Risk_Aggregator_Agent` | 2 | N | N | Y |
| `Trend_Reporting_Agent` | 2 | Y | Y | Y |

## 6. Orchestration, Guardrails, and Autonomy Cluster

| Agent | Count | Essentials | Plus | Enterprise |
|---|---:|:---:|:---:|:---:|
| `Swarm_Orchestrator_Agent` | 1 | Y | Y | Y |
| `Trend_Orchestrator_Agent` | 1 | N | N | Y |
| `Trigger_Router_Agent` | 2 | N | N | Y |
| `Execution_Contract_Agent` | 2 | N | N | Y |
| `Drift_Guardrail_Agent` | 2 | N | N | Y |
| `RBAC_Enforcer_Agent` | 1 | N | N | Y |
| `Tenant_Isolation_Agent` | 1 | N | N | Y |

## 7. High-Level Summary

| Cluster | Essentials | Plus | Enterprise |
|---|---|---|---|
| Ingestion and normalization | Basic | Full | Full |
| Features and embeddings | Basic | Full | Full + quality |
| Trend pipeline | Basic | Full | Full + advanced baselines |
| Anomaly, drift, forecast | None | Full | Full + campaign intelligence |
| Risk and reporting | Reporting only | Full | Full + tenant aggregation |
| Orchestration and guardrails | Minimal | Minimal | Full autonomy layer |

This matrix is the product packaging bridge between the technical swarm and customer-facing tiers.

