"""AFE ledger — monotonic attributed burn (§10 / §6 ledger fuzz target)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


class LedgerError(ValueError):
    """Illegal ledger mutation rejected fail-closed."""


@dataclass
class ReplenishEvent:
    actor: str
    amount: int
    signature: str

    def valid(self) -> bool:
        if self.amount <= 0 or not self.actor:
            return False
        digest = hashlib.sha256(f"{self.actor}:{self.amount}".encode()).hexdigest()
        return self.signature == digest[:16]


@dataclass
class AfeLedger:
    balance: int
    _initial_balance: int = field(init=False, repr=False)
    entries: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.balance < 0:
            raise LedgerError("initial balance must be non-negative")
        self._initial_balance = self.balance

    def apply_burn(self, actor: str, amount: int) -> None:
        if not actor:
            raise LedgerError("burn requires attributed actor")
        if amount <= 0:
            raise LedgerError("burn amount must be positive")
        if amount > self.balance:
            raise LedgerError("burn exceeds balance")
        self.balance -= amount
        self.entries.append({"type": "burn", "actor": actor, "amount": amount, "balance": self.balance})

    def apply_replenish(self, event: ReplenishEvent) -> None:
        if not event.valid():
            raise LedgerError("unsigned or invalid replenish event")
        self.balance += event.amount
        self.entries.append(
            {"type": "replenish", "actor": event.actor, "amount": event.amount, "balance": self.balance}
        )

    def monotonic(self) -> bool:
        """Balance never exceeds initial + signed replenishments."""
        allowed_max = self._initial_balance
        for entry in self.entries:
            if entry["type"] == "replenish":
                allowed_max += entry["amount"]
            if entry["balance"] > allowed_max:
                return False
        return self.balance <= allowed_max
