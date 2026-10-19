from datetime import datetime, timedelta

from units.celsius import Celsius
from units.hourly_period import HourlyPeriod
from units.hourly_weather import HourlyWeather


class WeatherForecast:
    @classmethod
    def create(cls, raw_forecast: list | None) -> "WeatherForecast":
        periods = []

        if raw_forecast is not None:
            for item in raw_forecast:
                if not isinstance(item, dict):
                    continue
                if not all(key in item for key in ["datetime", "temperature", "humidity"]):
                    continue
                try:
                    periods.append(
                        HourlyWeather(
                            period=HourlyPeriod.parse(item["datetime"]),
                            temperature=Celsius(float(item["temperature"])),
                            humidity=float(item["humidity"]),
                        )
                    )
                except (ValueError, TypeError, KeyError):
                    continue

        return cls(periods)

    def __init__(self, periods: list[HourlyWeather]) -> None:
        self.periods = periods

    def find_by_datetime(self, dt: datetime) -> HourlyWeather | None:
        for period in self.periods:
            if period.period.start == dt:
                return period
        return None

    def hourly(
        self,
        period_start: datetime,
        period_hours: int,
        temperature_fallback: Celsius,
        humidity_fallback: float,
    ) -> list[HourlyWeather]:
        periods = []
        for hour_offset in range(period_hours):
            current = period_start + timedelta(hours=hour_offset)
            weather = self.find_by_datetime(current)
            if weather is None:
                weather = HourlyWeather(
                    period=HourlyPeriod(current),
                    temperature=temperature_fallback,
                    humidity=humidity_fallback,
                )
            periods.append(weather)
        return periods
