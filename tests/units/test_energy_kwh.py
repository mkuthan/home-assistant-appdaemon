import pytest
from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh


@pytest.mark.parametrize(
    "energy_value",
    [
        -50.5,
        0.0,
        50.5,
    ],
)
def test_valid_energy(energy_value: float) -> None:
    energy = EnergyKwh(energy_value)
    assert energy.value == energy_value


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (-50.0, 30.0, -20.0),
        (0.0, 50.0, 50.0),
        (25.5, 24.5, 50.0),
    ],
)
def test_add(energy1: float, energy2: float, expected: float) -> None:
    result = EnergyKwh(energy1) + EnergyKwh(energy2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (-50.0, 30.0, -80.0),
        (0.0, 50.0, -50.0),
        (25.5, 24.5, 1.0),
    ],
)
def test_sub(energy1: float, energy2: float, expected: float) -> None:
    result = EnergyKwh(energy1) - EnergyKwh(energy2)
    assert result.value == expected


def test_div() -> None:
    energy1 = EnergyKwh(10.0)
    energy2 = EnergyKwh(2.0)
    assert energy1 / energy2 == 5.0


def test_div_by_zero() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero energy"):
        EnergyKwh(10.0) / ENERGY_KWH_ZERO  # pyright: ignore[reportUnusedExpression]


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (50.0, 100.0, True),
        (0.0, 50.0, True),
        (50.0, 50.0, False),
        (100.0, 50.0, False),
    ],
)
def test_less_than(energy1: float, energy2: float, expected: bool) -> None:
    result = EnergyKwh(energy1) < EnergyKwh(energy2)
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
    result = EnergyKwh(energy1) <= EnergyKwh(energy2)
    assert result == expected


@pytest.mark.parametrize(
    ("energy1", "energy2", "expected"),
    [
        (100.0, 50.0, True),
        (50.0, 0.0, True),
        (50.0, 50.0, False),
        (50.0, 100.0, False),
    ],
)
def test_greater_than(energy1: float, energy2: float, expected: bool) -> None:
    result = EnergyKwh(energy1) > EnergyKwh(energy2)
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
    result = EnergyKwh(energy1) >= EnergyKwh(energy2)
    assert result == expected


@pytest.mark.parametrize(
    ("energy_value", "expected"),
    [
        (50.0, "50.00kWh"),
        (0.0, "0.00kWh"),
        (-0.0, "0.00kWh"),
    ],
)
def test_str(energy_value: float, expected: str) -> None:
    energy = EnergyKwh(energy_value)
    assert f"{energy}" == expected
