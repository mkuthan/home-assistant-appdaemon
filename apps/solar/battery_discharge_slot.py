from dataclasses import dataclass
from datetime import time

from units.battery_current import BatteryCurrent


@dataclass(frozen=True)
class BatteryDischargeSlot:
    start_time: time
    end_time: time
    current: BatteryCurrent

    def time_str(self) -> str:
        start_time_str = self.start_time.strftime("%H:%M")
        end_time_str = self.end_time.strftime("%H:%M")
        return f"{start_time_str}-{end_time_str}"

    def __str__(self) -> str:
        return f"{self.time_str()}@{self.current}"

    @classmethod
    def from_time_str(cls, time_str: str, current: BatteryCurrent) -> "BatteryDischargeSlot":
        start_str, end_str = time_str.split("-")
        return cls(
            start_time=time.fromisoformat(start_str),
            end_time=time.fromisoformat(end_str),
            current=current,
        )
