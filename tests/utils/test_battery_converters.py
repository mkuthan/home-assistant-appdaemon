import pytest
from units.battery_current import BatteryCurrent
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh
from utils.battery_converters import current_to_energy_kwh, energy_kwh_to_current


@pytest.mark.parametrize(
    ("current_value", "voltage_value", "duration_hours", "expected_energy"),
    [
        (10.0, 50.0, 1, 0.5),
        (20.0, 100.0, 2, 4.0),
    ],
)
def test_current_to_energy_kwh(
    current_value: float, voltage_value: float, duration_hours: int, expected_energy: float
) -> None:
    current = BatteryCurrent(value=current_value)
    voltage = BatteryVoltage(value=voltage_value)

    result = current_to_energy_kwh(current, voltage, duration_hours=duration_hours)

    assert result == EnergyKwh(value=expected_energy)


@pytest.mark.parametrize("duration_hours", [0, -1])
def test_current_to_energy_kwh_raises_error_when_duration_is_not_positive(duration_hours: int) -> None:
    current = BatteryCurrent(value=10.0)
    voltage = BatteryVoltage(value=50.0)

    with pytest.raises(ValueError, match="Duration must be positive"):
        current_to_energy_kwh(current, voltage, duration_hours=duration_hours)


@pytest.mark.parametrize(
    ("energy_value", "voltage_value", "duration_hours", "expected_current"),
    [
        (0.5, 50.0, 1, 10.0),
        (4.0, 100.0, 2, 20.0),
    ],
)
def test_energy_kwh_to_current(
    energy_value: float, voltage_value: float, duration_hours: int, expected_current: float
) -> None:
    energy = EnergyKwh(value=energy_value)
    voltage = BatteryVoltage(value=voltage_value)

    result = energy_kwh_to_current(energy, voltage, duration_hours=duration_hours)

    assert result == BatteryCurrent(value=expected_current)


@pytest.mark.parametrize("duration_hours", [0, -1])
def test_energy_kwh_to_current_raises_error_when_duration_is_not_positive(duration_hours: int) -> None:
    energy = EnergyKwh(value=0.5)
    voltage = BatteryVoltage(value=50.0)

    with pytest.raises(ValueError, match="Duration must be positive"):
        energy_kwh_to_current(energy, voltage, duration_hours=duration_hours)
