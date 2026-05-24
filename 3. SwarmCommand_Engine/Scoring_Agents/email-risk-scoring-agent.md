# Email Risk Scoring Agent

SwarmCommand Engine — Scoring Layer

## Purpose

Assign a numerical risk score to an email based on detection signals.

## Inputs

- Sender mismatch score

- Link domain risk score

- Urgency language score

- Executive impersonation score

- Layout anomaly score

## Outputs

- Total risk score (0–30)

- Classification (Low / Medium / High)

- Signal breakdown

## Behaviors

- Normalize incoming signals

- Apply weighted scoring

- Flag high‑risk combinations

- Pass results to Analysis Layer

## Notes

This agent does not detect — it only scores.

