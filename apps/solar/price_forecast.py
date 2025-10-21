from datetime import datetime, timedelta

from units.energy_price import EnergyPrice
from units.hourly_period import HourlyPeriod
from units.hourly_price import HourlyPrice


class PriceForecast:
    @staticmethod
    def create(raw_forecast: object) -> "PriceForecast":
        periods = []

        if raw_forecast and isinstance(raw_forecast, list):
            for item in raw_forecast:
                if not isinstance(item, dict):
                    continue
                if not all(key in item for key in ["hour", "price"]):
                    continue

                try:
                    periods.append(
                        HourlyPrice(
                            period=HourlyPeriod.parse(item["hour"]),
                            price=EnergyPrice.pln_per_mwh(item["price"]),
                        )
                    )
                except (ValueError, TypeError, KeyError):
                    continue

        return PriceForecast(periods)

    def __init__(self, periods: list[HourlyPrice]) -> None:
        self.periods = periods

    def find_peak_periods(
        self, period_start: datetime, period_hours: int, price_threshold: EnergyPrice
    ) -> list[HourlyPrice]:
        period_end = period_start + timedelta(hours=period_hours)
        relevant_periods = [
            p for p in self.periods if period_start <= p.period.start <= period_end and p.price >= price_threshold
        ]
        return relevant_periods

    def find_daily_min_price(self, period_start: datetime, period_hours: int) -> EnergyPrice | None:
        period_end = period_start + timedelta(hours=period_hours)
        daily_prices = [p.price for p in self.periods if period_start <= p.period.start <= period_end]
        if not daily_prices:
            return None

        return min(daily_prices)
