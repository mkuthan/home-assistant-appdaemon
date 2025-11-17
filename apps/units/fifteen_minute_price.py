from dataclasses import dataclass

from units.energy_price import EnergyPrice
from units.fifteen_minute_period import FifteenMinutePeriod


@dataclass(frozen=True)
class FifteenMinutePrice:
    period: FifteenMinutePeriod
    price: EnergyPrice

    def __str__(self) -> str:
        return f"{self.period} {self.price}"
