"""Pytest path setup — expose the flat chaos modules like the runtime does.

The kinetic/chaos modules import each other flatly (e.g. `from kinetic_telemetry
import ...`) after inserting the chaos dir on sys.path. Tests do the same.
"""

import sys
from pathlib import Path

CHAOS = Path(__file__).resolve().parents[1] / "mmi" / "project_brain" / "chaos"
if str(CHAOS) not in sys.path:
    sys.path.insert(0, str(CHAOS))
