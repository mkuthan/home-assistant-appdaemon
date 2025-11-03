from datetime import UTC, datetime

import pytest
from units.celsius import Celsius
from units.hourly_period import HourlyPeriod
from units.hourly_weather import HourlyWeather
from utils.temperature_estimators import estimate_temperature_decay_time

DECAY_RATE = 0.0226  # hour⁻¹


@pytest.mark.parametrize(
    ("temp_start", "temp_end", "outdoor_temps", "expected_hours"),
    [
        # Simple constant outdoor temperature
        (Celsius(22.9), Celsius(21.3), [8.0] * 10, 5.03),
        (Celsius(22.9), Celsius(20.5), [8.0] * 10, 7.77),
        (Celsius(22.9), Celsius(19.9), [8.0] * 15, 9.95),
        # Already at target
        (Celsius(20.0), Celsius(20.0), [8.0] * 10, 0.0),
        # Target warmer than start
        (Celsius(20.0), Celsius(22.0), [8.0] * 10, 0.0),
        # Varying outdoor temperatures (getting colder - faster decay with lower outdoor temp)
        (Celsius(20.0), Celsius(18.0), [10.0, 8.0, 6.0, 4.0], 4.0),
        # Varying outdoor temperatures (getting warmer - slower decay with higher outdoor temp)
        (Celsius(20.0), Celsius(18.0), [5.0, 6.0, 7.0, 8.0], 4.0),
        # Large temperature drop
        (Celsius(25.0), Celsius(20.0), [5.0] * 20, 12.8),
        # Small temperature drop with warm outdoor temp (slower decay)
        (Celsius(22.0), Celsius(21.0), [15.0] * 5, 5.0),
        # Target reached mid-hour (very small temperature drop)
        (Celsius(22.0), Celsius(21.5), [8.0], 1.0),
    ],
)
def test_estimate_temperature_decay_time(
    temp_start: Celsius,
    temp_end: Celsius,
    outdoor_temps: list[float],
    expected_hours: float,
) -> None:
    base_time = datetime.fromisoformat("2025-01-01T00:00:00+00:00")
    hourly_weather = [
        HourlyWeather(
            period=HourlyPeriod(start=base_time.replace(hour=i)),
            temperature=temp,
            humidity=50.0,
        )
        for i, temp in enumerate(outdoor_temps)
    ]

    result = estimate_temperature_decay_time(temp_start, temp_end, hourly_weather, DECAY_RATE)

    assert result.total_seconds() == pytest.approx(expected_hours * 3600, rel=1e-2)


def test_estimate_temperature_decay_time_outdoor_warmer_than_current() -> None:
    temp_start = Celsius(20.0)
    temp_end = Celsius(18.0)
    base_time = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    hourly_weather = [
        HourlyWeather(
            period=HourlyPeriod(start=base_time),
            temperature=18.0,
            humidity=50.0,
        ),
        HourlyWeather(
            period=HourlyPeriod(start=base_time.replace(hour=1)),
            temperature=20.0,
            humidity=50.0,
        ),
    ]

    result = estimate_temperature_decay_time(temp_start, temp_end, hourly_weather, DECAY_RATE)

    # Should stop when outdoor becomes warmer
    assert result.total_seconds() == pytest.approx(3600.0, rel=1e-2)


def test_estimate_temperature_decay_time_invalid_decay_rate() -> None:
    temp_start = Celsius(22.0)
    temp_end = Celsius(20.0)
    base_time = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    hourly_weather = [HourlyWeather(period=HourlyPeriod(start=base_time), temperature=8.0, humidity=50.0)]

    with pytest.raises(ValueError, match="Decay rate must be positive"):
        estimate_temperature_decay_time(temp_start, temp_end, hourly_weather, 0.0)

    with pytest.raises(ValueError, match="Decay rate must be positive"):
        estimate_temperature_decay_time(temp_start, temp_end, hourly_weather, -0.01)


def test_estimate_temperature_decay_time_empty_weather_list() -> None:
    temp_start = Celsius(22.0)
    temp_end = Celsius(20.0)
    hourly_weather: list[HourlyWeather] = []

    result = estimate_temperature_decay_time(temp_start, temp_end, hourly_weather, DECAY_RATE)

    assert result.total_seconds() == 0.0
