from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, order=True)
class BatteryVoltage:
    _ZERO_VALUE: ClassVar[float] = 0.0

    value: float

    def __post_init__(self) -> None:
        if self.value < self._ZERO_VALUE:
            raise ValueError(f"Battery voltage must be non-negative, got {self.value}")

    def __str__(self) -> str:
        return f"{self.value:.2f}V"


BATTERY_VOLTAGE_ZERO = BatteryVoltage(BatteryVoltage._ZERO_VALUE)
