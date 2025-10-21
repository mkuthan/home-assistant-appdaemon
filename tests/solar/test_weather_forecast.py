from datetime import datetime

import pytest
from solar.weather_forecast import HourlyWeather, WeatherForecast
from units.hourly_period import HourlyPeriod


def test_create() -> None:
    # Home Assistant weather forecast format
    raw_forecast = {
        "weather.forecast_wieprz": {
            "forecast": [
                {
                    "datetime": "2025-10-03T14:00:00+00:00",
                    "temperature": 12.0,
                    "humidity": 46.0,
                },
                {
                    "datetime": "2025-10-03T15:00:00+00:00",
                    "temperature": 13.0,
                    "humidity": 45.0,
                },
            ]
        }
    }

    forecast_weather = WeatherForecast.create(raw_forecast)

    assert forecast_weather.periods == [
        HourlyWeather(
            period=HourlyPeriod.parse("2025-10-03T14:00:00+00:00"),
            temperature=12.0,
            humidity=46.0,
        ),
        HourlyWeather(
            period=HourlyPeriod.parse("2025-10-03T15:00:00+00:00"),
            temperature=13.0,
            humidity=45.0,
        ),
    ]


@pytest.fixture
def forecast_weather() -> WeatherForecast:
    return WeatherForecast(
        [
            HourlyWeather(
                period=HourlyPeriod.parse("2025-10-03T14:00:00+00:00"),
                temperature=12.0,
                humidity=46.0,
            ),
            HourlyWeather(
                period=HourlyPeriod.parse("2025-10-03T15:00:00+00:00"),
                temperature=13.0,
                humidity=45.0,
            ),
        ]
    )


def test_find_by_datetime_found(forecast_weather: WeatherForecast) -> None:
    dt = datetime.fromisoformat("2025-10-03T15:00:00+00:00")

    result = forecast_weather.find_by_datetime(dt)

    assert result == HourlyWeather(
        period=HourlyPeriod(dt),
        temperature=13.0,
        humidity=45.0,
    )


def test_find_by_datetime_not_found(forecast_weather: WeatherForecast) -> None:
    dt = datetime.fromisoformat("2025-10-03T16:00:00+00:00")

    result = forecast_weather.find_by_datetime(dt)

    assert result is None


def test_find_by_datetime_empty_periods() -> None:
    dt = datetime.fromisoformat("2025-10-03T15:00:00+00:00")
    forecast_weather = WeatherForecast([])

    result = forecast_weather.find_by_datetime(dt)

    assert result is None
