import pytest
from units.battery_voltage import BatteryVoltage


@pytest.mark.parametrize(
    "voltage_value",
    [
        0.0,
        12.5,
        100.0,
    ],
)
def test_valid_voltage(voltage_value: float) -> None:
    voltage = BatteryVoltage(value=voltage_value)
    assert voltage.value == voltage_value


@pytest.mark.parametrize(
    "voltage_value",
    [
        -1.0,
        -12.0,
        -100.0,
    ],
)
def test_invalid_voltage(voltage_value: float) -> None:
    with pytest.raises(ValueError, match=f"Battery voltage must be non-negative, got {voltage_value}"):
        BatteryVoltage(value=voltage_value)


@pytest.mark.parametrize(
    ("voltage1", "voltage2", "expected"),
    [
        (5.0, 10.0, True),
        (5.0, 5.0, False),
        (10.0, 5.0, False),
    ],
)
def test_less_than(voltage1: float, voltage2: float, expected: bool) -> None:
    result = BatteryVoltage(value=voltage1) < BatteryVoltage(value=voltage2)
    assert result == expected


@pytest.mark.parametrize(
    ("voltage1", "voltage2", "expected"),
    [
        (5.0, 10.0, True),
        (5.0, 5.0, True),
        (10.0, 5.0, False),
    ],
)
def test_less_than_or_equal(voltage1: float, voltage2: float, expected: bool) -> None:
    result = BatteryVoltage(value=voltage1) <= BatteryVoltage(value=voltage2)
    assert result == expected


@pytest.mark.parametrize(
    ("voltage1", "voltage2", "expected"),
    [
        (10.0, 5.0, True),
        (5.0, 5.0, False),
        (5.0, 10.0, False),
    ],
)
def test_greater_than(voltage1: float, voltage2: float, expected: bool) -> None:
    result = BatteryVoltage(value=voltage1) > BatteryVoltage(value=voltage2)
    assert result == expected


@pytest.mark.parametrize(
    ("voltage1", "voltage2", "expected"),
    [
        (10.0, 5.0, True),
        (5.0, 5.0, True),
        (5.0, 10.0, False),
    ],
)
def test_greater_than_or_equal(voltage1: float, voltage2: float, expected: bool) -> None:
    result = BatteryVoltage(value=voltage1) >= BatteryVoltage(value=voltage2)
    assert result == expected


@pytest.mark.parametrize(
    ("voltage1", "voltage2", "expected"),
    [
        (10.0, 10.0, True),
        (0.0, 0.0, True),
        (10.0, 10.1, False),
    ],
)
def test_equality(voltage1: float, voltage2: float, expected: bool) -> None:
    result = BatteryVoltage(value=voltage1) == BatteryVoltage(value=voltage2)
    assert result == expected


def test_equality_with_non_battery_voltage() -> None:
    voltage = BatteryVoltage(value=10.0)
    assert (voltage == 10.0) is False
    assert (voltage == "10") is False
    assert (voltage == object()) is False


def test_format() -> None:
    voltage = BatteryVoltage(value=12.3456)
    assert f"{voltage}" == "12.35V"
