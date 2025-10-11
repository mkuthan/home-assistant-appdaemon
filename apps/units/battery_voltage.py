from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class BatteryVoltage:
    _ZERO_VALUE: ClassVar[float] = 0.0

    value: float

    def __post_init__(self) -> None:
        if self.value < self._ZERO_VALUE:
            raise ValueError(f"Battery voltage must be non-negative, got {self.value}")

    def __lt__(self, other: "BatteryVoltage") -> bool:
        return self.value < other.value

    def __le__(self, other: "BatteryVoltage") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "BatteryVoltage") -> bool:
        return self.value > other.value

    def __ge__(self, other: "BatteryVoltage") -> bool:
        return self.value >= other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BatteryVoltage):
            return NotImplemented
        return self.value == other.value

    def __format__(self, _format_spec: str) -> str:
        return f"{self.value:.2f}V"


BATTERY_VOLTAGE_ZERO = BatteryVoltage(BatteryVoltage._ZERO_VALUE)
