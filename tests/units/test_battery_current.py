import pytest
from units.battery_current import BatteryCurrent


@pytest.mark.parametrize(
    "current_value",
    [
        0.0,
        10.5,
        100.0,
    ],
)
def test_valid_current(current_value: float) -> None:
    current = BatteryCurrent(value=current_value)
    assert current.value == current_value


@pytest.mark.parametrize(
    "current_value",
    [
        -1.0,
        -10.0,
        -100.0,
    ],
)
def test_invalid_current(current_value: float) -> None:
    with pytest.raises(ValueError, match=f"Battery current must be non-negative, got {current_value}"):
        BatteryCurrent(value=current_value)


@pytest.mark.parametrize(
    ("current1", "current2", "expected"),
    [
        (5.0, 10.0, True),
        (5.0, 5.0, False),
        (10.0, 5.0, False),
    ],
)
def test_less_than(current1: float, current2: float, expected: bool) -> None:
    result = BatteryCurrent(value=current1) < BatteryCurrent(value=current2)
    assert result == expected


@pytest.mark.parametrize(
    ("current1", "current2", "expected"),
    [
        (5.0, 10.0, True),
        (5.0, 5.0, True),
        (10.0, 5.0, False),
    ],
)
def test_less_than_or_equal(current1: float, current2: float, expected: bool) -> None:
    result = BatteryCurrent(value=current1) <= BatteryCurrent(value=current2)
    assert result == expected


@pytest.mark.parametrize(
    ("current1", "current2", "expected"),
    [
        (10.0, 5.0, True),
        (5.0, 5.0, False),
        (5.0, 10.0, False),
    ],
)
def test_greater_than(current1: float, current2: float, expected: bool) -> None:
    result = BatteryCurrent(value=current1) > BatteryCurrent(value=current2)
    assert result == expected


@pytest.mark.parametrize(
    ("current1", "current2", "expected"),
    [
        (10.0, 5.0, True),
        (5.0, 5.0, True),
        (5.0, 10.0, False),
    ],
)
def test_greater_than_or_equal(current1: float, current2: float, expected: bool) -> None:
    result = BatteryCurrent(value=current1) >= BatteryCurrent(value=current2)
    assert result == expected


@pytest.mark.parametrize(
    ("current1", "current2", "expected"),
    [
        (10.0, 10.0, True),
        (0.0, 0.0, True),
        (10.0, 10.1, False),
    ],
)
def test_equality(current1: float, current2: float, expected: bool) -> None:
    result = BatteryCurrent(value=current1) == BatteryCurrent(value=current2)
    assert result == expected


def test_equality_with_non_battery_current() -> None:
    current = BatteryCurrent(value=10.0)
    assert (current == 10.0) is False
    assert (current == "10") is False
    assert (current == object()) is False


def test_format() -> None:
    current = BatteryCurrent(value=12.3456)
    assert f"{current}" == "12.35A"
