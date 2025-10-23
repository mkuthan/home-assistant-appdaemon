from decimal import Decimal

import pytest
from units.battery_soc import BatterySoc


@pytest.mark.parametrize(
    "soc_value",
    [
        Decimal("0.0"),
        Decimal("50.5"),
        Decimal("100.0"),
    ],
)
def test_valid_soc(soc_value: Decimal) -> None:
    soc = BatterySoc(value=soc_value)
    assert soc.value == soc_value


@pytest.mark.parametrize(
    "soc_value",
    [
        Decimal("-1.0"),
        Decimal("100.1"),
        Decimal("200.0"),
    ],
)
def test_invalid_soc(soc_value: Decimal) -> None:
    with pytest.raises(ValueError, match=f"Battery SOC must be between 0.0 and 100.0, got {soc_value}"):
        BatterySoc(value=soc_value)


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (Decimal("50.0"), Decimal("30.0"), Decimal("80.0")),
        (Decimal("0.0"), Decimal("50.0"), Decimal("50.0")),
        (Decimal("50.0"), Decimal("60.0"), Decimal("100.0")),  # Caps at 100%
    ],
)
def test_add(soc1: Decimal, soc2: Decimal, expected: Decimal) -> None:
    result = BatterySoc(value=soc1) + BatterySoc(value=soc2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (Decimal("80.0"), Decimal("30.0"), Decimal("50.0")),
        (Decimal("50.0"), Decimal("0.0"), Decimal("50.0")),
        (Decimal("30.0"), Decimal("50.0"), Decimal("0.0")),  # Caps at 0%
    ],
)
def test_sub(soc1: Decimal, soc2: Decimal, expected: Decimal) -> None:
    result = BatterySoc(value=soc1) - BatterySoc(value=soc2)
    assert result.value == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (Decimal("50.0"), Decimal("100.0"), True),
        (Decimal("50.0"), Decimal("50.0"), False),
        (Decimal("100.0"), Decimal("50.0"), False),
    ],
)
def test_less_than(soc1: Decimal, soc2: Decimal, expected: bool) -> None:
    result = BatterySoc(value=soc1) < BatterySoc(value=soc2)
    assert result == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (Decimal("50.0"), Decimal("100.0"), True),
        (Decimal("0.0"), Decimal("50.0"), True),
        (Decimal("50.0"), Decimal("50.0"), True),
        (Decimal("100.0"), Decimal("50.0"), False),
    ],
)
def test_less_than_or_equal(soc1: Decimal, soc2: Decimal, expected: bool) -> None:
    result = BatterySoc(value=soc1) <= BatterySoc(value=soc2)
    assert result == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (Decimal("100.0"), Decimal("50.0"), True),
        (Decimal("50.0"), Decimal("50.0"), False),
        (Decimal("50.0"), Decimal("100.0"), False),
    ],
)
def test_greater_than(soc1: Decimal, soc2: Decimal, expected: bool) -> None:
    result = BatterySoc(value=soc1) > BatterySoc(value=soc2)
    assert result == expected


@pytest.mark.parametrize(
    ("soc1", "soc2", "expected"),
    [
        (Decimal("100.0"), Decimal("50.0"), True),
        (Decimal("50.0"), Decimal("0.0"), True),
        (Decimal("50.0"), Decimal("50.0"), True),
        (Decimal("50.0"), Decimal("100.0"), False),
    ],
)
def test_greater_than_or_equal(soc1: Decimal, soc2: Decimal, expected: bool) -> None:
    result = BatterySoc(value=soc1) >= BatterySoc(value=soc2)
    assert result == expected


def test_str() -> None:
    soc = BatterySoc(value=Decimal("75.4567"))
    assert f"{soc}" == "75.46%"


def test_value_is_decimal() -> None:
    soc = BatterySoc(value=Decimal("50.0"))
    assert isinstance(soc.value, Decimal)
    assert soc.value == Decimal("50.0")
