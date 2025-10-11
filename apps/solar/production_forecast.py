from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh


@dataclass(frozen=True)
class ProductionForecastPeriod:
    datetime: datetime
    energy: EnergyKwh


class ProductionForecast(Protocol):
    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh: ...


class ProductionForecastComposite:
    def __init__(self, *components: ProductionForecast) -> None:
        self.components = components

    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        total_energy_kwh = ENERGY_KWH_ZERO
        for component in self.components:
            total_energy_kwh += component.estimate_energy_kwh(period_start, period_hours)
        return total_energy_kwh


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
                        ProductionForecastPeriod(
                            datetime=datetime.fromisoformat(item["period_start"]),
                            energy=EnergyKwh(item["pv_estimate"]),
                        )
                    )
                except (ValueError, TypeError, KeyError):
                    continue

        return ProductionForecastDefault(periods)

    def __init__(self, periods: list[ProductionForecastPeriod]) -> None:
        self.periods = periods

    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        period_end = period_start + timedelta(hours=period_hours)
        total_energy_kwh = ENERGY_KWH_ZERO

        for period in self.periods:
            if period_start <= period.datetime < period_end:
                total_energy_kwh += period.energy
        return total_energy_kwh
