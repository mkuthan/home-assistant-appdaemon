from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class BatteryCurrent:
    _ZERO_VALUE: ClassVar[float] = 0.0

    value: float

    def __post_init__(self) -> None:
        if self.value < self._ZERO_VALUE:
            raise ValueError(f"Battery current must be non-negative, got {self.value}")

    def __add__(self, other: "BatteryCurrent") -> "BatteryCurrent":
        return BatteryCurrent(self.value + other.value)

    def __sub__(self, other: "BatteryCurrent") -> "BatteryCurrent":
        return BatteryCurrent(max(self._ZERO_VALUE, self.value - other.value))

    def __lt__(self, other: "BatteryCurrent") -> bool:
        return self.value < other.value

    def __le__(self, other: "BatteryCurrent") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "BatteryCurrent") -> bool:
        return self.value > other.value

    def __ge__(self, other: "BatteryCurrent") -> bool:
        return self.value >= other.value

    def __str__(self) -> str:
        return f"{self.value:.2f}A"


BATTERY_CURRENT_ZERO = BatteryCurrent(BatteryCurrent._ZERO_VALUE)
