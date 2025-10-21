from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HourlyPeriod:
    start: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None:
            raise ValueError("Hourly period start must be timezone-aware")

        if self.start.minute != 0 or self.start.second != 0 or self.start.microsecond != 0:
            raise ValueError(f"Hourly period start must be at the beginning of an hour, got {self.start.isoformat()}")

    def __str__(self) -> str:
        return self.start.isoformat()
