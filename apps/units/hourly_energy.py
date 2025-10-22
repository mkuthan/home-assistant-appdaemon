from dataclasses import dataclass
from typing import Self

from units.energy_kwh import EnergyKwh
from units.hourly_period import HourlyPeriod


class HourlyEnergyStrMixin:
    period: HourlyPeriod
    energy: EnergyKwh

    def __str__(self) -> str:
        return f"{self.period} {self.energy}"

    @classmethod
    def format_list(cls, energies: list[Self], separator: str = ", ") -> str:
        return f"[{separator.join(str(energy) for energy in energies)}]"


@dataclass(frozen=True)
class HourlyConsumptionEnergy(HourlyEnergyStrMixin):
    period: HourlyPeriod
    energy: EnergyKwh


@dataclass(frozen=True)
class HourlyProductionEnergy(HourlyEnergyStrMixin):
    period: HourlyPeriod
    energy: EnergyKwh


@dataclass(frozen=True)
class HourlyNetEnergy(HourlyEnergyStrMixin):
    period: HourlyPeriod
    energy: EnergyKwh
