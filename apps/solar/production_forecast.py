from datetime import datetime, timedelta
from typing import Protocol

from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh
from units.hourly_energy import HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


class ProductionForecast(Protocol):
    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]: ...

    def total(self, period_start: datetime, period_hours: int) -> EnergyKwh: ...


class ProductionForecastComposite:
    def __init__(self, *components: ProductionForecast) -> None:
        self.components = components

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]:
        return [item for component in self.components for item in component.hourly(period_start, period_hours)]

    def total(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        total_energy = ENERGY_KWH_ZERO

        for component in self.components:
            total_energy += component.total(period_start, period_hours)

        return total_energy


# Solar production forecast based on Solcast integration
class ProductionForecastDefault:
    @classmethod
    def create(cls, raw_forecast: list) -> "ProductionForecastDefault":
        periods = []

        for item in raw_forecast:
            if not isinstance(item, dict):
                continue
            if not all(key in item for key in ["period_start", "pv_estimate"]):
                continue

            try:
                periods.append(
                    HourlyProductionEnergy(
                        period=HourlyPeriod.parse(item["period_start"]),
                        energy=EnergyKwh(item["pv_estimate"]),
                    )
                )
            except (ValueError, TypeError, KeyError):
                continue

        return cls(periods)

    def __init__(self, periods: list[HourlyProductionEnergy]) -> None:
        self.periods = periods

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]:
        period_end = period_start + timedelta(hours=period_hours)
        return [period for period in self.periods if period_start <= period.period.start < period_end]

    def total(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        total_energy = ENERGY_KWH_ZERO

        for period in self.hourly(period_start, period_hours):
            total_energy += period.energy

        return total_energy
