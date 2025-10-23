from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


@dataclass(frozen=True)
class BatterySoc:
    _MIN_VALUE: ClassVar[Decimal] = Decimal("0.0")
    _MAX_VALUE: ClassVar[Decimal] = Decimal("100.0")

    value: Decimal

    def __init__(self, value: Decimal | float | str) -> None:
        # Convert value to Decimal if it's not already
        if not isinstance(value, Decimal):
            value = Decimal(str(value))

        # Use object.__setattr__ since we're frozen
        object.__setattr__(self, "value", value)

        # Validate
        if not self._MIN_VALUE <= self.value <= self._MAX_VALUE:
            raise ValueError(f"Battery SOC must be between {self._MIN_VALUE} and {self._MAX_VALUE}, got {self.value}")

    def __add__(self, other: BatterySoc) -> BatterySoc:
        return BatterySoc(value=min(self.value + other.value, self._MAX_VALUE))

    def __sub__(self, other: BatterySoc) -> BatterySoc:
        return BatterySoc(value=max(self.value - other.value, self._MIN_VALUE))

    def __lt__(self, other: BatterySoc) -> bool:
        return self.value < other.value

    def __le__(self, other: BatterySoc) -> bool:
        return self.value <= other.value

    def __gt__(self, other: BatterySoc) -> bool:
        return self.value > other.value

    def __ge__(self, other: BatterySoc) -> bool:
        return self.value >= other.value

    def __str__(self) -> str:
        return f"{self.value:.2f}%"


BATTERY_SOC_MIN = BatterySoc(BatterySoc._MIN_VALUE)
BATTERY_SOC_MAX = BatterySoc(BatterySoc._MAX_VALUE)
