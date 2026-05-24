# Signal Library — Experimental Notes

SwarmCommand Engine — Detection Sandbox

## Purpose

To document experimental “signals” that may later be used by SwarmCommand detection agents.

## Current Experimental Signals

### 1. Sender Mismatch Score

- Compare display name vs domain

- Flag look‑alike domains

- Score: 0–5

### 2. Link Domain Risk Score

- Check for unfamiliar domains

- Check for hyphens, numbers, or odd TLDs

- Score: 0–10

### 3. Urgency Language Detector

- “ASAP”, “urgent”, “right away”, “before my meeting”

- Score: 0–5

### 4. Executive Impersonation Indicators

- Short messages

- Vague requests

- Unusual timing

- Score: 0–10

### 5. Layout & Structure Anomalies

- Missing signatures

- Odd spacing

- Generic greetings

- Score: 0–5

## Notes

These signals are **experimental only** and not validated for production.

