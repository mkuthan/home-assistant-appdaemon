from datetime import datetime, timedelta
from typing import Protocol

from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


class ProductionForecast(Protocol):
    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]: ...


class ProductionForecastComposite:
    def __init__(self, *components: ProductionForecast) -> None:
        self.components = components

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]:
        return [item for component in self.components for item in component.hourly(period_start, period_hours)]


class ProductionForecastDefault:
    @staticmethod
    def create(raw_forecast: object) -> "ProductionForecastDefault":
        periods = []

        if raw_forecast and isinstance(raw_forecast, list):
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

        return ProductionForecastDefault(periods)

    def __init__(self, periods: list[HourlyProductionEnergy]) -> None:
        self.periods = periods

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]:
        period_end = period_start + timedelta(hours=period_hours)
        return [period for period in self.periods if period_start <= period.period.start < period_end]
