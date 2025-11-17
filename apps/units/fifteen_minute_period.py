from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass(frozen=True)
class FifteenMinutePeriod:
    start: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None:
            raise ValueError("Fifteen minute period start must be timezone-aware")

        if self.start.minute % 15 != 0 or self.start.second != 0 or self.start.microsecond != 0:
            msg = (
                f"Fifteen minute period start must be at the beginning of a 15-minute interval, "
                f"got {self.start.isoformat()}"
            )
            raise ValueError(msg)

    def __str__(self) -> str:
        return self.start.isoformat()

    def start_time(self) -> time:
        return self.start.time()

    def end_time(self) -> time:
        return (self.start + timedelta(minutes=15)).time()

    @classmethod
    def parse(cls, date_string: str) -> "FifteenMinutePeriod":
        return cls(start=datetime.fromisoformat(date_string))
