from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WeatherForecastPeriod:
    datetime: datetime
    temperature: float
    humidity: float


class WeatherForecast:
    @staticmethod
    def create(raw_forecast: object) -> "WeatherForecast":
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
                                WeatherForecastPeriod(
                                    datetime=datetime.fromisoformat(item["datetime"]),
                                    temperature=float(item["temperature"]),
                                    humidity=float(item["humidity"]),
                                )
                            )
                        except (ValueError, TypeError, KeyError):
                            continue

        return WeatherForecast(periods)

    def __init__(self, periods: list[WeatherForecastPeriod]) -> None:
        self.periods = periods

    def find_by_datetime(self, dt: datetime) -> WeatherForecastPeriod | None:
        for period in self.periods:
            if period.datetime == dt:
                return period
        return None
