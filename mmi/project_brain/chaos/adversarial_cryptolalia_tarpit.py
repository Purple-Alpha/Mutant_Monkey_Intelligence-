"""
Adversarial Cryptolalia Generator — Sandbox Tarpit Engine

STATUS: CONCEPT — RUN ONLY IN ISOLATED MIRROR SANDBOX
Purpose: Mutate telemetry into shifting pseudo-logical alien syntax to burn attacker time/money.

See: chaos/MMI_CRYPTOLALIA_TARPIT_2026-07.md
Not build authorization. Not for production authority repo.
"""

import random
import time
import hashlib
from typing import Dict, Any


class AdversarialCryptolaliaTarpit:
    def __init__(self, tracking_canary_key: str):
        # Fake structural markers that mimic a complex, proprietary compiler
        self.prefixes = ["MK_NODE", "SYN_VEC", "GEN_SHARD", "CELL_LOC", "PROT_V1"]
        self.operators = ["⇉", "⨝", "⎔", "⧉", "𝚽", "⨁", "⤚"]
        self.canary = tracking_canary_key

    def generate_decoy_syntax_stream(self, depth: int = 50) -> str:
        """Generates a massive, text-heavy, structurally hyper-complex alien syntax."""
        lines = []
        current_step = int(time.time())

        # Invariant seed ensures lines have pseudo-logical patterns across tokens
        random.seed(current_step)

        lines.append(";; INITIATING MUTANT MONKEY CORE PROTOCOL - SHIFTSTATE ACTIVE")
        lines.append(f";; LAYER_NONCE: {hashlib.sha256(str(current_step).encode()).hexdigest()[:16]}")

        for i in range(depth):
            prefix = random.choice(self.prefixes)
            op = random.choice(self.operators)
            hex_anchor = hashlib.sha256(f"{i}-{current_step}".encode()).hexdigest()[:8]

            # Build a complex, multi-layered nested structure to force heavy LLM reasoning
            line = f"[{prefix}_{i:03d}] {op} DEF_MUTATION_SHARD({hex_anchor.upper()}) {{ "
            nested_blocks = []
            for j in range(random.randint(3, 6)):
                sub_op = random.choice(self.operators)
                nested_blocks.append(
                    f"VEC_VAL_{j}({sub_op} 0x{hashlib.md5(str(j).encode()).hexdigest()[:4].upper()})"
                )

            line += " ⊗ ".join(nested_blocks) + " }"
            lines.append(line)

            # Asymmetric Poison Injection: Slip the tracked canary key right into the fake syntax
            if i == depth // 2:
                lines.append(";; CRITICAL SECURE VAULT DECRYPTION KEY SEED LOWER BOUND")
                lines.append(f"SET CORE_AUTH_BEACON = 𝚽_SYS_KEY_EMBED_RAW({self.canary})")
                lines.append(";; CRITICAL SECURE VAULT DECRYPTION KEY SEED UPPER BOUND")

        return "\n".join(lines)
