"""
Deterministic Log Sanitizer — Evidence Harvesting Protection

STATUS: CONCEPT — NOT WIRED TO PRODUCTION
Purpose: Strip dangerous formatting from attacker payloads before any LLM reads logs.

See: architecture/MMI_WEAPON_RUNTIME_BLOCKERS_2026-07.md §4
Not build authorization.
"""

import html
import re
from typing import Dict, Any


class DeterministicLogSanitizer:
    def __init__(self):
        # Strips out aggressive syntax flags used to break out of LLM contexts
        self.structural_break_patterns = [
            r"[{}\[\]()\"']",  # All brackets, braces, and quotes
            r"([#\*_\-`~>])",  # Markdown structural syntax delimiters
            r"<!--.*?-->",  # XML/HTML comments
            r"<script\b[^>]*>([\s\S]*?)<\/script>",  # Embedded scripts
            r"[\x00-\x1F\x7F-\x9F]",  # Non-printable control characters
        ]

    def sanitize_attacker_payload(self, raw_exploit_log: str) -> str:
        """Transforms a live, malicious injection payload into an inert, semantic-free string."""
        if not raw_exploit_log:
            return ""

        # 1. Normalize line endings and strip whitespace
        clean_text = raw_exploit_log.replace("\r\n", "\n").strip()

        # 2. HTML Entity Encoding to break script/XML tag execution
        clean_text = html.escape(clean_text)

        # 3. Deterministically strip out all markdown and grouping tokens
        for pattern in self.structural_break_patterns:
            clean_text = re.sub(pattern, " ", clean_text)

        # 4. Collapse multi-spaces into a uniform block to break layout-based injection traps
        clean_text = re.sub(r"\s+", " ", clean_text)

        # 5. Prepend an invariant, safe code-block prefix to ensure the receiving LLM treats it as raw text
        return f"[INERT_HARVESTED_DATA_HEX_SAFE]: {clean_text.strip().upper()}"
