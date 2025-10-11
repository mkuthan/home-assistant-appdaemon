import pytest
from utils.hvac_estimators import estimate_heating_energy_consumption


def test_heating_energy_consumption_at_reference_temperature() -> None:
    t_out = 7.0
    t_in = 20.0
    humidity = 50.0
    cop_at_7c = 4.0
    h = 0.18

    result = estimate_heating_energy_consumption(t_out, t_in, humidity, cop_at_7c, h)

    # (0.18 * 13) / 4.0 = 0.585 kW
    assert result.value == pytest.approx(0.585, rel=1e-6)


def test_heating_energy_consumption_cold_weather() -> None:
    t_out = -10.0
    t_in = 20.0
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
    t_out = 15.0
    t_in = 20.0
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
    t_out = 3.5
    t_in = 20.0
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
    t_out = 20.0
    t_in = 20.0
    humidity = 50.0
    cop_at_7c = 4.0
    h = 0.18

    result = estimate_heating_energy_consumption(t_out, t_in, humidity, cop_at_7c, h)

    assert result.value == 0.0
