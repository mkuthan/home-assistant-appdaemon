import pytest
from units.celsius import Celsius


@pytest.mark.parametrize(
    "temperature_value",
    [
        -40.0,
        -10.5,
        0.0,
        20.5,
        40.0,
    ],
)
def test_valid_temperature(temperature_value: float) -> None:
    temperature = Celsius(temperature_value)
    assert temperature.value == temperature_value


@pytest.mark.parametrize(
    ("temp1", "temp2", "expected"),
    [
        (-10.0, 5.0, -5.0),
        (0.0, 20.0, 20.0),
        (15.5, 4.5, 20.0),
    ],
)
def test_add(temp1: float, temp2: float, expected: float) -> None:
    result = Celsius(temp1) + Celsius(temp2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("temp1", "temp2", "expected"),
    [
        (-10.0, 5.0, -15.0),
        (0.0, 20.0, -20.0),
        (25.5, 5.5, 20.0),
    ],
)
def test_sub(temp1: float, temp2: float, expected: float) -> None:
    result = Celsius(temp1) - Celsius(temp2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("temp1", "temp2", "expected"),
    [
        (-10.0, 0.0, True),
        (0.0, 20.0, True),
        (20.0, 20.0, False),
        (30.0, 20.0, False),
    ],
)
def test_less_than(temp1: float, temp2: float, expected: bool) -> None:
    result = Celsius(temp1) < Celsius(temp2)
    assert result == expected


@pytest.mark.parametrize(
    ("temp1", "temp2", "expected"),
    [
        (-10.0, 0.0, True),
        (0.0, 20.0, True),
        (20.0, 20.0, True),
        (30.0, 20.0, False),
    ],
)
def test_less_than_or_equal(temp1: float, temp2: float, expected: bool) -> None:
    result = Celsius(temp1) <= Celsius(temp2)
    assert result == expected


@pytest.mark.parametrize(
    ("temp1", "temp2", "expected"),
    [
        (-10.0, 0.0, False),
        (0.0, 20.0, False),
        (20.0, 20.0, False),
        (30.0, 20.0, True),
    ],
)
def test_greater_than(temp1: float, temp2: float, expected: bool) -> None:
    result = Celsius(temp1) > Celsius(temp2)
    assert result == expected


@pytest.mark.parametrize(
    ("temp1", "temp2", "expected"),
    [
        (-10.0, 0.0, False),
        (0.0, 20.0, False),
        (20.0, 20.0, True),
        (30.0, 20.0, True),
    ],
)
def test_greater_than_or_equal(temp1: float, temp2: float, expected: bool) -> None:
    result = Celsius(temp1) >= Celsius(temp2)
    assert result == expected


@pytest.mark.parametrize(
    ("temp_value", "expected_value"),
    [
        (0.0, 0.0),
        (20.5, 21.0),
        (21.5, 22.0),
        (-10.3, -10.0),
    ],
)
def test_round(temp_value: float, expected_value: float) -> None:
    temp = Celsius(temp_value)
    rounded_temp = round(temp)
    assert rounded_temp.value == expected_value


@pytest.mark.parametrize(
    ("temp_value", "expected_str"),
    [
        (0.0, "0.0°C"),
        (20.5, "20.5°C"),
        (-10.3, "-10.3°C"),
    ],
)
def test_str(temp_value: float, expected_str: str) -> None:
    temp = Celsius(temp_value)
    assert str(temp) == expected_str
