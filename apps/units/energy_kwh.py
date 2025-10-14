from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class EnergyKwh:
    _ZERO_VALUE: ClassVar[float] = 0.0

    value: float

    def __post_init__(self) -> None:
        if self.value < self._ZERO_VALUE:
            raise ValueError(f"Energy must be non-negative, got {self.value}")

    def __add__(self, other: "EnergyKwh") -> "EnergyKwh":
        return EnergyKwh(value=self.value + other.value)

    def __sub__(self, other: "EnergyKwh") -> "EnergyKwh":
        return EnergyKwh(value=max(self.value - other.value, self._ZERO_VALUE))

    def __mul__(self, other: float) -> "EnergyKwh":
        if other < self._ZERO_VALUE:
            raise ValueError(f"Multiplier must be non-negative, got {other}")
        return EnergyKwh(value=self.value * other)

    def __truediv__(self, other: float) -> "EnergyKwh":
        if other <= self._ZERO_VALUE:
            raise ValueError(f"Divisor must be positive, got {other}")
        return EnergyKwh(value=self.value / other)

    def __lt__(self, other: "EnergyKwh") -> bool:
        return self.value < other.value

    def __le__(self, other: "EnergyKwh") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "EnergyKwh") -> bool:
        return self.value > other.value

    def __ge__(self, other: "EnergyKwh") -> bool:
        return self.value >= other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnergyKwh):
            return NotImplemented
        return self.value == other.value

    def __format__(self, _format_spec: str) -> str:
        return f"{self.value:.2f}kWh"

    def ratio(self, other: "EnergyKwh") -> float:
        if other == ENERGY_KWH_ZERO:
            raise ValueError("Cannot divide by zero energy")
        return self.value / other.value


ENERGY_KWH_ZERO = EnergyKwh(EnergyKwh._ZERO_VALUE)
