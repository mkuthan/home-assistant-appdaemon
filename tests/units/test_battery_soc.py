import pytest
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh


@pytest.mark.parametrize(
    "soc_value",
    [
        0.0,
        50.5,
        100.0,
    ],
)
def test_valid_soc(soc_value: float) -> None:
    soc = BatterySoc(value=soc_value)
    assert soc.value == soc_value


@pytest.mark.parametrize(
    "soc_value",
    [
        -1.0,
        100.1,
        200.0,
    ],
)
def test_invalid_soc(soc_value: float) -> None:
    with pytest.raises(ValueError, match=f"Battery SOC must be between 0.0 and 100.0, got {soc_value}"):
        BatterySoc(value=soc_value)


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (50.0, 30.0, 80.0),
        (0.0, 50.0, 50.0),
        (50.0, 60.0, 100.0),  # Caps at 100
    ],
)
def test_add(soc1: float, soc2: float, expected: float) -> None:
    result = BatterySoc(value=soc1) + BatterySoc(value=soc2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (80.0, 30.0, 50.0),
        (50.0, 0.0, 50.0),
        (30.0, 50.0, 0.0),  # Caps at 0
    ],
)
def test_sub(soc1: float, soc2: float, expected: float) -> None:
    result = BatterySoc(value=soc1) - BatterySoc(value=soc2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (50.0, 100.0, True),
        (50.0, 50.0, False),
        (100.0, 50.0, False),
    ],
)
def test_less_than(soc1: float, soc2: float, expected: bool) -> None:
    result = BatterySoc(value=soc1) < BatterySoc(value=soc2)
    assert result == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (50.0, 100.0, True),
        (0.0, 50.0, True),
        (50.0, 50.0, True),
        (100.0, 50.0, False),
    ],
)
def test_less_than_or_equal(soc1: float, soc2: float, expected: bool) -> None:
    result = BatterySoc(value=soc1) <= BatterySoc(value=soc2)
    assert result == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (100.0, 50.0, True),
        (50.0, 50.0, False),
        (50.0, 100.0, False),
    ],
)
def test_greater_than(soc1: float, soc2: float, expected: bool) -> None:
    result = BatterySoc(value=soc1) > BatterySoc(value=soc2)
    assert result == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (100.0, 50.0, True),
        (50.0, 0.0, True),
        (50.0, 50.0, True),
        (50.0, 100.0, False),
    ],
)
def test_greater_than_or_equal(soc1: float, soc2: float, expected: bool) -> None:
    result = BatterySoc(value=soc1) >= BatterySoc(value=soc2)
    assert result == expected


def test_str() -> None:
    soc = BatterySoc(value=75.4567)
    assert f"{soc}" == "75.46%"


@pytest.mark.parametrize(
    ("soc_value", "battery_capacity", "expected_energy"),
    [
        (50.0, 10.0, 5.0),
        (100.0, 10.0, 10.0),
        (0.0, 10.0, 0.0),
    ],
)
def test_to_energy_kwh(soc_value: float, battery_capacity: float, expected_energy: float) -> None:
    soc = BatterySoc(value=soc_value)
    capacity = EnergyKwh(value=battery_capacity)
    result = soc.to_energy_kwh(capacity)
    assert result.value == pytest.approx(expected_energy)
