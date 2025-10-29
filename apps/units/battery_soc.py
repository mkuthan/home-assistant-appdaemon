from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, order=True)
class BatterySoc:
    _MIN_VALUE: ClassVar[float] = 0.0
    _MAX_VALUE: ClassVar[float] = 100.0

    value: float

    def __post_init__(self) -> None:
        if not self._MIN_VALUE <= self.value <= self._MAX_VALUE:
            raise ValueError(f"Battery SOC must be between {self._MIN_VALUE} and {self._MAX_VALUE}, got {self.value}")

    def __add__(self, other: "BatterySoc") -> "BatterySoc":
        return BatterySoc(value=min(self.value + other.value, self._MAX_VALUE))

    def __sub__(self, other: "BatterySoc") -> "BatterySoc":
        return BatterySoc(value=max(self.value - other.value, self._MIN_VALUE))

    def __str__(self) -> str:
        return f"{self.value:.2f}%"


BATTERY_SOC_MIN = BatterySoc(BatterySoc._MIN_VALUE)
BATTERY_SOC_MAX = BatterySoc(BatterySoc._MAX_VALUE)
