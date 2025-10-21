from datetime import datetime, timedelta
from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh
from units.hourly_energy import HourlyEnergyAggregator, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


class ProductionForecast(Protocol):
    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh: ...
    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]: ...


class ProductionForecastComposite:
    def __init__(self, appdaemon_logger: AppdaemonLogger, *components: ProductionForecast) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.components = components

    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        total_energy_kwh = ENERGY_KWH_ZERO
        for component in self.components:
            energy_kwh = component.estimate_energy_kwh(period_start, period_hours)
            if energy_kwh > ENERGY_KWH_ZERO:
                name = component.__class__.__name__
                self.appdaemon_logger.info(f"Estimated energy production ({name}): {energy_kwh}")
                total_energy_kwh += energy_kwh
        return total_energy_kwh

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]:
        total = [item for component in self.components for item in component.hourly(period_start, period_hours)]
        return HourlyEnergyAggregator.aggregate_hourly_production(total)


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
                            period=HourlyPeriod(datetime.fromisoformat(item["period_start"])),
                            energy=EnergyKwh(item["pv_estimate"]),
                        )
                    )
                except (ValueError, TypeError, KeyError):
                    continue

        return ProductionForecastDefault(periods)

    def __init__(self, periods: list[HourlyProductionEnergy]) -> None:
        self.periods = periods

    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        period_end = period_start + timedelta(hours=period_hours)
        total_energy_kwh = ENERGY_KWH_ZERO

        for period in self.periods:
            if period_start <= period.period.start < period_end:
                total_energy_kwh += period.energy
        return total_energy_kwh

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyProductionEnergy]:
        period_end = period_start + timedelta(hours=period_hours)
        return [period for period in self.periods if period_start <= period.period.start < period_end]
