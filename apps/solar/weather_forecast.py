from datetime import datetime

from units.hourly_period import HourlyPeriod
from units.hourly_weather import HourlyWeather


class WeatherForecast:
    @classmethod
    def create(cls, raw_forecast: object) -> "WeatherForecast":
        periods = []

        if raw_forecast and isinstance(raw_forecast, dict):
            weather_data = raw_forecast.get("weather.forecast_wieprz", {})
            if isinstance(weather_data, dict):
                forecast_list = weather_data.get("forecast")

                if forecast_list and isinstance(forecast_list, list):
                    for item in forecast_list:
                        if not isinstance(item, dict):
                            continue
                        if not all(key in item for key in ["datetime", "temperature", "humidity"]):
                            continue
                        try:
                            periods.append(
                                HourlyWeather(
                                    period=HourlyPeriod.parse(item["datetime"]),
                                    temperature=float(item["temperature"]),
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
