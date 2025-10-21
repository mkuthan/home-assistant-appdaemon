from units.hourly_period import HourlyPeriod
from units.hourly_weather import HourlyWeather


def test_str() -> None:
    weather = HourlyWeather(
        period=HourlyPeriod.parse("2025-11-15T09:00:00+00:00"),
        temperature=22.5,
        humidity=55.0,
    )

    assert f"{weather}" == "2025-11-15T09:00:00+00:00 22.5C 55.0%"
