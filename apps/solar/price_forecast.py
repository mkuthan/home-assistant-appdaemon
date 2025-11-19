from datetime import datetime, timedelta
from decimal import Decimal
from itertools import groupby

from units.energy_price import EnergyPrice
from units.fifteen_minute_period import FifteenMinutePeriod
from units.fifteen_minute_price import FifteenMinutePrice
from units.hourly_period import HourlyPeriod
from units.hourly_price import HourlyPrice
from utils.time_utils import truncate_to_hour


class PriceForecast:
    @classmethod
    def create_from_rce_15_mins(cls, raw_forecast: list | None, time_zone: str) -> "PriceForecast":
        periods = []

        if raw_forecast is not None:
            for item in raw_forecast:
                if not isinstance(item, dict):
                    continue
                if not all(key in item for key in ["dtime", "rce_pln"]):
                    continue

                try:
                    periods.append(
                        FifteenMinutePrice(
                            period=FifteenMinutePeriod.parse_custom(
                                item["dtime"], format="%Y-%m-%d %H:%M:%S", time_zone=time_zone
                            ),
                            price=EnergyPrice.pln_per_mwh(Decimal(str(item["rce_pln"]))),
                        )
                    )
                except (ValueError, TypeError, KeyError):
                    continue

        return cls(periods)

    def __init__(self, periods: list[FifteenMinutePrice]) -> None:
        self.periods = periods
        self.hourly_periods = [
            HourlyPrice(
                period=HourlyPeriod(start=hour),
                price=sum(prices[1:], start=prices[0]) / Decimal(len(prices)),
            )
            for hour, group in groupby(periods, key=lambda p: truncate_to_hour(p.period.start))
            if (prices := [p.price.non_negative() for p in group])
        ]

    def find_min_hour(self, period_start: datetime, period_hours: int) -> HourlyPrice | None:
        period_end = period_start + timedelta(hours=period_hours)
        hourly_prices = [
            hourly_period
            for hourly_period in self.hourly_periods
            if period_start <= hourly_period.period.start < period_end
        ]
        if not hourly_prices:
            return None

        return min(hourly_prices, key=lambda p: p.price)

    def select_hourly_prices(self, period_start: datetime, period_end: datetime) -> list[HourlyPrice]:
        return [
            hourly_period
            for hourly_period in self.hourly_periods
            if period_start <= hourly_period.period.start < period_end
        ]
