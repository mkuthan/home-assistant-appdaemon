from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, order=True)
class EnergyKwh:
    _ZERO_VALUE: ClassVar[float] = 0.0

    value: float

    def __add__(self, other: "EnergyKwh") -> "EnergyKwh":
        return EnergyKwh(value=self.value + other.value)

    def __sub__(self, other: "EnergyKwh") -> "EnergyKwh":
        return EnergyKwh(value=self.value - other.value)

    def __truediv__(self, other: "EnergyKwh") -> float:
        if other == ENERGY_KWH_ZERO:
            raise ValueError("Cannot divide by zero energy")
        return self.value / other.value

    def __neg__(self) -> "EnergyKwh":
        return EnergyKwh(value=-self.value)

    def __str__(self) -> str:
        return f"{self.value:.2f}kWh"


ENERGY_KWH_ZERO = EnergyKwh(EnergyKwh._ZERO_VALUE)
