from datetime import datetime, timedelta
from decimal import Decimal

from units.energy_price import EnergyPrice
from units.hourly_period import HourlyPeriod
from units.hourly_price import HourlyPrice
from utils.time_utils import truncate_to_hour


class PriceForecast:
    @classmethod
    def create_from_rce_15_mins(cls, raw_forecast: list | None) -> "PriceForecast":
        periods = []

        if raw_forecast is not None:
            hourly_data: dict[datetime, list[Decimal]] = {}

            for item in raw_forecast:
                if not isinstance(item, dict):
                    continue
                if not all(key in item for key in ["dtime", "rce_pln"]):
                    continue

                try:
                    dtime = datetime.fromisoformat(item["dtime"])
                    dtime_hour = truncate_to_hour(dtime)

                    rce_pln = max(Decimal(str(item["rce_pln"])), Decimal("0"))

                    if dtime_hour not in hourly_data:
                        hourly_data[dtime_hour] = []
                    hourly_data[dtime_hour].append(rce_pln)
                except (ValueError, TypeError, KeyError):
                    continue

            for dtime_hour in sorted(hourly_data.keys()):
                prices = hourly_data[dtime_hour]
                avg_price = sum(prices) / Decimal(len(prices))

                periods.append(
                    HourlyPrice(
                        period=HourlyPeriod(dtime_hour),
                        price=EnergyPrice.pln_per_mwh(avg_price),
                    )
                )

        return cls(periods)

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
