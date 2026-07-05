# Codex Handoff — Iceberg Layer 4 Build

**Task id:** `mmi-iceberg-l4-behavioral-fingerprint-build`  
**Spec:** `architecture/MMI_ICEBERG_L4_BEHAVIORAL_FINGERPRINT_SPEC_2026-07.md` (PASS)  
**Build auth:** NOT_AUTHORIZED until Matt says authorize build

Stop prompt at `def analyze_fingerprint(` — paste header + class shell, let Codex complete body only.

---

```python
# ==============================================================================
# MMI SYSTEM SPECIFICATION COMPILER — ICEBERG LAYER 4
# DESTINATION: mmi/project_brain/chaos/behavioral_fingerprint_layer.py
# SPEC: architecture/MMI_ICEBERG_L4_BEHAVIORAL_FINGERPRINT_SPEC_2026-07.md
# ==============================================================================
"""
CONSTRAINTS:
1. Explicit type hints on all parameters and returns.
2. No broad except Exception — TypeError, ValueError, OSError, json.JSONDecodeError only.
3. Byte metrics from signed metadata["volumetric"]["payload_byte_size"] — not len(str).
4. Return key "detail" (singular), never "details".
5. ANOMALY: ok=True, verdict=ANOMALY, route=MIRROR_DIMENSION — never hard-drop.
6. COLD_START: count < N (default 20) — record only, ok=True, verdict=COLD_START.
7. Persistence: atomic JSON via tempfile + os.replace (_NonceStore pattern).

INPUT:
  sender_id: str
  metadata: dict  # post-signature trusted
  payload: dict   # sibling field, verified hash-bound

OUTPUT:
  tuple[bool, dict] — always includes verdict; anomaly adds route=MIRROR_DIMENSION

INTEGRATION (separate file edit):
  metadata_ingress_gate.admit() after L6 — if route MIRROR_DIMENSION, divert not reject.

NON-GOALS: L5, L7, L9, raw payload log, ML training.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_COLD_START_N = 20
DEFAULT_K_STDEV = 4.0
DEFAULT_MIN_CAPABILITY_FREQ = 0.02


class BehavioralFingerprintLayer:
    def __init__(
        self,
        state_path: Path | None = None,
        cold_start_n: int = DEFAULT_COLD_START_N,
        k_stdev: float = DEFAULT_K_STDEV,
        min_capability_freq: float = DEFAULT_MIN_CAPABILITY_FREQ,
    ) -> None:
        ...

    def analyze_fingerprint(
        self,
        sender_id: str,
        metadata: dict[str, Any],
        payload: dict[str, Any],
    ) -> tuple[bool, dict[str, Any]]:
```

Also deliver: `tests/test_behavioral_fingerprint_layer.py` covering spec T1-T3.

Hard stops: MMI only; no L5; wire gate only if spec integration block is followed exactly.
