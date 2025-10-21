from dataclasses import dataclass

from units.energy_price import EnergyPrice
from units.hourly_period import HourlyPeriod


@dataclass(frozen=True)
class HourlyPrice:
    period: HourlyPeriod
    price: EnergyPrice

    def __str__(self) -> str:
        return f"{self.period} {self.price}"
