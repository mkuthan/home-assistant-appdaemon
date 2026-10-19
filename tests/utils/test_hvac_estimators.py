from datetime import datetime, timedelta

import pytest
from units.celsius import Celsius
from units.hourly_period import HourlyPeriod
from units.hourly_weather import HourlyWeather
from utils.hvac_estimators import estimate_heating_energy_consumption, estimate_heating_idle_until

DECAY_RATE = 0.0226  # hour⁻¹


def test_heating_energy_consumption_at_reference_temperature() -> None:
    t_out = Celsius(7.0)
    t_in = Celsius(20.0)
    humidity = 50.0
    cop_at_7c = 4.0
    h = 0.18

    result = estimate_heating_energy_consumption(t_out, t_in, humidity, cop_at_7c, h)

    # (0.18 * 13) / 4.0 = 0.585 kW
    assert result.value == pytest.approx(0.585, rel=1e-6)


def test_heating_energy_consumption_cold_weather() -> None:
    t_out = Celsius(-10.0)
    t_in = Celsius(20.0)
    humidity = 50.0
    cop_at_7c = 4.0
    h = 0.18

    result = estimate_heating_energy_consumption(t_out, t_in, humidity, cop_at_7c, h)

    # Then consumption should be higher due to lower COP at cold temps
    # Temperature coefficient at -10°C: 1 + (-10 - 7) * 0.033 = 0.439 (clamped to 0.5)
    # Adjusted COP: 4.0 * 0.5 * 1.0 = 2.0
    # Consumption: (0.18 * 30) / 2.0 = 2.7 kW
    assert result.value == pytest.approx(2.7, rel=1e-9)


def test_heating_energy_consumption_mild_weather() -> None:
    t_out = Celsius(15.0)
    t_in = Celsius(20.0)
    humidity = 50.0
    cop_at_7c = 4.0
    h = 0.18

    result = estimate_heating_energy_consumption(t_out, t_in, humidity, cop_at_7c, h)

    # Then consumption should be lower due to higher COP at mild temps
    # Temperature coefficient at 15°C: 1 + (15 - 7) * 0.033 = 1.264
    # Adjusted COP: 4.0 * 1.264 * 1.0 = 5.056
    # Consumption: (0.18 * 5) / 5.056 ≈ 0.178 kW
    assert result.value == pytest.approx(0.178, rel=1e-2)


def test_heating_energy_consumption_with_frosting_penalty() -> None:
    t_out = Celsius(3.5)
    t_in = Celsius(20.0)
    humidity = 100.0
    cop_at_7c = 4.0
    h = 0.18

    result = estimate_heating_energy_consumption(t_out, t_in, humidity, cop_at_7c, h)

    # Then consumption should include frosting penalty
    # Temperature coefficient: 1 + (3.5 - 7) * 0.033 = 0.8845
    # Frosting penalty at worst frosting point: 1 - 0.15 * 1.0 * 1.0 = 0.85
    # Adjusted COP: 4.0 * 0.8845 * 0.85 = 3.007
    # Consumption: (0.18 * 16.5) / 3.007 ≈ 0.987 kW
    assert result.value == pytest.approx(0.987, rel=1e-2)


def test_heating_energy_consumption_no_heating_needed() -> None:
    t_out = Celsius(20.0)
    t_in = Celsius(20.0)
    humidity = 50.0
    cop_at_7c = 4.0
    h = 0.18

    result = estimate_heating_energy_consumption(t_out, t_in, humidity, cop_at_7c, h)

    assert result.value == 0.0


@pytest.fixture
def constant_hourly_weather() -> list[HourlyWeather]:
    start = datetime.fromisoformat("2025-01-01T14:00:00+00:00")
    return [
        HourlyWeather(period=HourlyPeriod(start + timedelta(hours=i)), temperature=Celsius(5.0), humidity=50.0)
        for i in range(24)
    ]


def test_estimate_heating_idle_until(constant_hourly_weather: list[HourlyWeather]) -> None:
    now = datetime.fromisoformat("2025-01-01T14:37:00+00:00")
    t_in_actual = Celsius(22.0)
    t_in_target = Celsius(20.0)

    result = estimate_heating_idle_until(now, t_in_actual, t_in_target, constant_hourly_weather, DECAY_RATE)

    # Decay from the current hour: ln((22 - 5) / (20 - 5)) / 0.0226 ≈ 5.54h
    assert result.isoformat(timespec="minutes") == "2025-01-01T19:32+00:00"


@pytest.mark.parametrize(
    "t_in_actual",
    [
        # At target
        Celsius(20.0),
        # Below target
        Celsius(19.0),
    ],
)
def test_estimate_heating_idle_until_no_excess(
    constant_hourly_weather: list[HourlyWeather],
    t_in_actual: Celsius,
) -> None:
    now = datetime.fromisoformat("2025-01-01T14:37:00+00:00")
    t_in_target = Celsius(20.0)

    result = estimate_heating_idle_until(now, t_in_actual, t_in_target, constant_hourly_weather, DECAY_RATE)

    assert result == datetime.fromisoformat("2025-01-01T14:00:00+00:00")


def test_estimate_heating_idle_until_excess_capped(constant_hourly_weather: list[HourlyWeather]) -> None:
    now = datetime.fromisoformat("2025-01-01T14:37:00+00:00")
    t_in_target = Celsius(20.0)

    result_at_cap = estimate_heating_idle_until(now, Celsius(25.0), t_in_target, constant_hourly_weather, DECAY_RATE)
    result_above_cap = estimate_heating_idle_until(now, Celsius(30.0), t_in_target, constant_hourly_weather, DECAY_RATE)

    assert result_above_cap == result_at_cap
