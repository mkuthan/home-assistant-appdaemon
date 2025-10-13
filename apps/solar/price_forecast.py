from dataclasses import dataclass
from datetime import datetime, time, timedelta

from units.energy_price import EnergyPrice


@dataclass(frozen=True)
class PriceForecastPeriod:
    datetime: datetime
    price: EnergyPrice

    def __format__(self, _format_spec: str) -> str:
        return f"{self.datetime.isoformat()} - {self.price}"

    def start_time(self) -> time:
        return self.datetime.time()

    def end_time(self) -> time:
        return (self.datetime + timedelta(hours=1)).time()


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
                        PriceForecastPeriod(
                            datetime=datetime.fromisoformat(item["hour"]),
                            price=EnergyPrice.pln_per_mwh(item["price"]),
                        )
                    )
                except (ValueError, TypeError, KeyError):
                    continue

        return PriceForecast(periods)

    def __init__(self, periods: list[PriceForecastPeriod]) -> None:
        self.periods = periods

    def find_peak_periods(
        self, period_start: datetime, period_hours: int, price_threshold: EnergyPrice
    ) -> list[PriceForecastPeriod]:
        period_end = period_start + timedelta(hours=period_hours)
        relevant_periods = [
            p for p in self.periods if period_start <= p.datetime <= period_end and p.price >= price_threshold
        ]
        return relevant_periods

    def find_daily_min_price(self, day: datetime) -> EnergyPrice | None:
        day_start = datetime(day.year, day.month, day.day, tzinfo=day.tzinfo)
        day_end = day_start + timedelta(days=1)

        daily_prices = [p.price for p in self.periods if day_start <= p.datetime < day_end]
        if not daily_prices:
            return None

        return min(daily_prices)
