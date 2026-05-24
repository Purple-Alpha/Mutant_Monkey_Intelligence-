# Prototype Detection Agent

SwarmCommand Engine — Experimental Draft

## Concept

A lightweight agent that assigns a preliminary risk score to an email based on experimental signals.

## Inputs

- Sender address

- Subject line

- Body text

- Link domains

## Outputs

- Risk score (0–30)

- Signal breakdown

- Suggested classification (Low / Medium / High)

## Example Scoring Logic (Experimental)

- Sender mismatch: 3

- Link domain risk: 7

- Urgency language: 2

- Executive impersonation: 5

- Layout anomalies: 1

Total: 18 → Medium Risk

## Notes

This agent is **not** part of the production SwarmCommand Engine.  
It exists only for experimentation and iteration.

