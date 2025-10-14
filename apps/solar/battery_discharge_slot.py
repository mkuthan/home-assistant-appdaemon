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

    def __format__(self, _format_spec: str) -> str:
        return f"{self.time_str()}@{self.current}"
