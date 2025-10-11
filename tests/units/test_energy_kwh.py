import pytest
from units.battery_current import BatteryCurrent
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh


@pytest.mark.parametrize(
    "energy_value",
    [
        0.0,
        50.5,
        100.0,
        1000.0,
    ],
)
def test_valid_energy(energy_value: float) -> None:
    energy = EnergyKwh(value=energy_value)
    assert energy.value == energy_value


@pytest.mark.parametrize(
    "energy_value",
    [
        -1.0,
        -0.1,
        -100.0,
    ],
)
def test_invalid_energy(energy_value: float) -> None:
    with pytest.raises(ValueError, match=f"Energy must be non-negative, got {energy_value}"):
        EnergyKwh(value=energy_value)


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (50.0, 30.0, 80.0),
        (0.0, 50.0, 50.0),
        (25.5, 24.5, 50.0),
        (100.0, 200.0, 300.0),
        (0.0, 0.0, 0.0),
    ],
)
def test_add_valid_energies(energy1: float, energy2: float, expected: float) -> None:
    result = EnergyKwh(value=energy1) + EnergyKwh(value=energy2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (80.0, 30.0, 50.0),
        (50.0, 0.0, 50.0),
        (100.0, 25.5, 74.5),
        (30.0, 50.0, 0.0),  # Caps at 0
        (0.0, 1.0, 0.0),  # Caps at 0
    ],
)
def test_subtract_valid_energies(energy1: float, energy2: float, expected: float) -> None:
    result = EnergyKwh(value=energy1) - EnergyKwh(value=energy2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("energy_value", "multiplier", "expected"),
    [
        (50.0, 2.0, 100.0),
        (100.0, 0.5, 50.0),
        (25.5, 2.0, 51.0),
        (100.0, 0.0, 0.0),
        (0.0, 5.0, 0.0),
        (10.0, 1.0, 10.0),
        (10.0, 0.1, 1.0),
    ],
)
def test_multiply_energy_by_float(energy_value: float, multiplier: float, expected: float) -> None:
    result = EnergyKwh(value=energy_value) * multiplier
    assert result.value == expected


@pytest.mark.parametrize(
    "multiplier",
    [
        -1.0,
        -0.1,
        -100.0,
    ],
)
def test_multiply_by_negative_float(multiplier: float) -> None:
    energy = EnergyKwh(value=50.0)
    with pytest.raises(ValueError, match=f"Multiplier must be non-negative, got {multiplier}"):
        energy * multiplier  # pyright: ignore[reportUnusedExpression]


@pytest.mark.parametrize(
    ("energy_value", "divisor", "expected"),
    [
        (100.0, 2.0, 50.0),
        (50.0, 0.5, 100.0),
        (100.0, 4.0, 25.0),
        (10.0, 1.0, 10.0),
        (1.0, 0.1, 10.0),
        (0.0, 5.0, 0.0),
    ],
)
def test_divide_energy_by_float(energy_value: float, divisor: float, expected: float) -> None:
    result = EnergyKwh(value=energy_value) / divisor
    assert result.value == expected


@pytest.mark.parametrize(
    "divisor",
    [
        0.0,
        -1.0,
        -0.1,
        -100.0,
    ],
)
def test_divide_by_invalid_float(divisor: float) -> None:
    energy = EnergyKwh(value=50.0)
    with pytest.raises(ValueError, match=f"Divisor must be positive, got {divisor}"):
        energy / divisor  # pyright: ignore[reportUnusedExpression]


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (50.0, 100.0, True),
        (0.0, 50.0, True),
        (25.5, 75.5, True),
        (50.0, 50.0, False),
        (100.0, 50.0, False),
    ],
)
def test_less_than(energy1: float, energy2: float, expected: bool) -> None:
    result = EnergyKwh(value=energy1) < EnergyKwh(value=energy2)
    assert result == expected


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (50.0, 100.0, True),
        (0.0, 50.0, True),
        (50.0, 50.0, True),
        (100.0, 50.0, False),
    ],
)
def test_less_than_or_equal(energy1: float, energy2: float, expected: bool) -> None:
    result = EnergyKwh(value=energy1) <= EnergyKwh(value=energy2)
    assert result == expected


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (100.0, 50.0, True),
        (50.0, 0.0, True),
        (75.5, 25.5, True),
        (50.0, 50.0, False),
        (50.0, 100.0, False),
    ],
)
def test_greater_than(energy1: float, energy2: float, expected: bool) -> None:
    result = EnergyKwh(value=energy1) > EnergyKwh(value=energy2)
    assert result == expected


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (100.0, 50.0, True),
        (50.0, 0.0, True),
        (50.0, 50.0, True),
        (50.0, 100.0, False),
    ],
)
def test_greater_than_or_equal(energy1: float, energy2: float, expected: bool) -> None:
    result = EnergyKwh(value=energy1) >= EnergyKwh(value=energy2)
    assert result == expected


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (50.0, 50.0, True),
        (0.0, 0.0, True),
        (100.0, 100.0, True),
        (50.0, 51.0, False),
        (0.0, 100.0, False),
    ],
)
def test_equality(energy1: float, energy2: float, expected: bool) -> None:
    result = EnergyKwh(value=energy1) == EnergyKwh(value=energy2)
    assert result == expected


def test_equality_with_non_energy_kwh() -> None:
    energy = EnergyKwh(value=50.0)
    assert (energy == 50.0) is False
    assert (energy == "50") is False
    assert (energy == object()) is False


def test_format() -> None:
    energy = EnergyKwh(value=75.4567)
    assert f"{energy}" == "75.46kWh"


def test_ratio() -> None:
    energy1 = EnergyKwh(10.0)
    energy2 = EnergyKwh(2.0)
    assert energy1.ratio(energy2) == 5.0


def test_ratio_divide_by_zero() -> None:
    energy1 = EnergyKwh(10.0)
    energy2 = EnergyKwh(0.0)
    with pytest.raises(ValueError, match="Cannot divide by zero energy"):
        energy1.ratio(energy2)


def test_to_battery_current() -> None:
    energy = EnergyKwh(5.0)
    voltage = BatteryVoltage(50.0)
    duration_hours = 2
    assert energy.to_battery_current(voltage, duration_hours) == BatteryCurrent(50.0)
