"""Canonical ``sender_domain`` normalization — Phase 3 Detection Swarm.

Governing contract
------------------
``4. Product_Roadmap/Phase3_Detection_Swarm_Agent_Design_Contract.md`` — §11
SIGNED 2026-06-10 (Matt Nichol), commit ``c522292`` — together with
``Phase3_Detection_Swarm_Contract_Amendment_1.md`` — §11 SIGNED 2026-06-11
(Matt Nichol), commit ``56e8b33``.

Amendment §B adds one additive field, ``sender_domain: str``, to ``sender_signal``
(#78 SenderHistoryAgent) and ``geo_signal`` (#79 GeoVelocityAgent). Both agents
MUST use this identical helper so the value is **byte-identical** for the Phase 4
ReconciliationAgent join key. The normalization order is transcribed verbatim
from the amendment §B.
"""

from __future__ import annotations


def normalize_sender_domain(raw: str | None) -> str:
    """Return the canonical, normalized sender domain per Amendment 1 §B.

    Order (verbatim from the signed amendment):
      1. Strip surrounding whitespace.
      2. Strip a trailing dot (root label): ``example.com.`` -> ``example.com``.
      3. Strip a ``:port`` suffix if present: ``mail.example.com:443`` -> ``mail.example.com``.
      4. Lowercase ASCII (DNS names are case-insensitive).
      5. IDNA encode (UTS-46) to the ASCII A-label / punycode form for IDNs.

    The full host is preserved (subdomains kept; not reduced to the registrable
    domain). ``None`` and empty input return ``""``. A non-str raises ``TypeError``
    so malformed input fails safe at the boundary rather than silently corrupting
    the correlation key.
    """

    if raw is None:
        return ""
    if not isinstance(raw, str):
        raise TypeError("sender_domain must be a string")

    # 1. strip whitespace, 2. strip trailing dot(s) (root label).
    name = raw.strip().rstrip(".")

    # 3. strip a single ``:port`` suffix (digits only) — leaves IPv6/edge cases alone.
    if ":" in name:
        head, _, tail = name.rpartition(":")
        if head and tail.isdigit():
            name = head

    # 4. lowercase ASCII.
    name = name.lower()
    if not name:
        return ""

    # 5. IDNA / punycode (UTS-46). Prefer the ``idna`` package (UTS-46); fall back
    # to the stdlib ``idna`` codec, then to the lowered ASCII form so a malformed
    # label degrades to a safe deterministic value rather than raising mid-write.
    try:
        import idna as _idna

        return _idna.encode(name, uts46=True).decode("ascii")
    except Exception:
        pass

    if all(ord(char) < 128 for char in name):
        return name

    try:
        return name.encode("idna").decode("ascii")
    except Exception:
        return name
