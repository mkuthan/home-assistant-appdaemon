import pytest
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from utils.battery_converters import energy_to_soc, soc_to_energy


@pytest.mark.parametrize(
    ("energy_value", "battery_capacity", "expected_soc"),
    [
        (0.0, 10.0, 0.0),
        (5.0, 10.0, 50.0),
        (10.0, 10.0, 100.0),
        (15.0, 10.0, 100.0),  # Caps at 100%
    ],
)
def test_energy_to_soc(energy_value: float, battery_capacity: float, expected_soc: float) -> None:
    energy = EnergyKwh(value=energy_value)
    capacity = EnergyKwh(value=battery_capacity)
    result = energy_to_soc(energy, capacity)
    assert result.value == pytest.approx(expected_soc)


@pytest.mark.parametrize(
    ("soc_value", "battery_capacity", "expected_energy"),
    [
        (50.0, 10.0, 5.0),
        (100.0, 10.0, 10.0),
        (0.0, 10.0, 0.0),
    ],
)
def test_soc_to_energy(soc_value: float, battery_capacity: float, expected_energy: float) -> None:
    soc = BatterySoc(value=soc_value)
    capacity = EnergyKwh(value=battery_capacity)
    result = soc_to_energy(soc, capacity)
    assert result.value == pytest.approx(expected_energy)
