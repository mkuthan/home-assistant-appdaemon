from dataclasses import dataclass

from units.energy_kwh import EnergyKwh
from units.hourly_period import HourlyPeriod


class HourlyEnergyStrMixin:
    period: HourlyPeriod
    energy: EnergyKwh

    def __str__(self) -> str:
        return f"{self.period} {self.energy}"


@dataclass(frozen=True)
class HourlyConsumptionEnergy(HourlyEnergyStrMixin):
    period: HourlyPeriod
    energy: EnergyKwh


@dataclass(frozen=True)
class HourlyProductionEnergy(HourlyEnergyStrMixin):
    period: HourlyPeriod
    energy: EnergyKwh
