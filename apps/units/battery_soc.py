from dataclasses import dataclass
from typing import ClassVar

from units.energy_kwh import EnergyKwh


@dataclass(frozen=True)
class BatterySoc:
    _MIN_VALUE: ClassVar[float] = 0.0
    _MAX_VALUE: ClassVar[float] = 100.0

    # TODO: use decimal
    value: float

    def __post_init__(self) -> None:
        if not self._MIN_VALUE <= self.value <= self._MAX_VALUE:
            raise ValueError(f"Battery SOC must be between {self._MIN_VALUE} and {self._MAX_VALUE}, got {self.value}")

    def __add__(self, other: "BatterySoc") -> "BatterySoc":
        return BatterySoc(value=min(self.value + other.value, self._MAX_VALUE))

    def __sub__(self, other: "BatterySoc") -> "BatterySoc":
        return BatterySoc(value=max(self.value - other.value, self._MIN_VALUE))

    def __lt__(self, other: "BatterySoc") -> bool:
        return self.value < other.value

    def __le__(self, other: "BatterySoc") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "BatterySoc") -> bool:
        return self.value > other.value

    def __ge__(self, other: "BatterySoc") -> bool:
        return self.value >= other.value

    def __str__(self) -> str:
        return f"{self.value:.2f}%"

    def to_energy_kwh(self, battery_capacity_kwh: EnergyKwh) -> EnergyKwh:
        return battery_capacity_kwh * (self.value / self._MAX_VALUE)

    @classmethod
    def from_energy_kwh(cls, energy_kwh: EnergyKwh, battery_capacity_kwh: EnergyKwh) -> "BatterySoc":
        ratio = energy_kwh.ratio(battery_capacity_kwh) * 100.0
        return BatterySoc(min(ratio, cls._MAX_VALUE))


BATTERY_SOC_MIN = BatterySoc(BatterySoc._MIN_VALUE)
BATTERY_SOC_MAX = BatterySoc(BatterySoc._MAX_VALUE)
