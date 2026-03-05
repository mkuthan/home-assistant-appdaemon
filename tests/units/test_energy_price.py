from collections.abc import Callable
from decimal import Decimal

import pytest
from units.energy_price import EnergyPrice
from units.money import Money


@pytest.mark.parametrize(
    ("factory", "unit"),
    [
        (EnergyPrice.per_mwh, "MWh"),
        (EnergyPrice.per_kwh, "kWh"),
    ],
)
def test_class_factory_method(factory: Callable[[Money], EnergyPrice], unit: str) -> None:
    money = Money.pln(Decimal("50.0"))
    price = factory(money)
    assert price.money == money
    assert price.unit == unit


@pytest.mark.parametrize(
    "unit",
    [
        "ABC",
        "XYZ",
    ],
)
def test_invalid_unit(unit: str) -> None:
    with pytest.raises(ValueError, match=f"Unsupported unit {unit}"):
        EnergyPrice(money=Money(Decimal(0), "PLN"), unit=unit)


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("100.5", "50.25", "150.75"),
        ("0.0", "0.0", "0.0"),
        ("123.45", "67.89", "191.34"),
    ],
)
def test_add(price1: str, price2: str, expected: str) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price1))) + EnergyPrice.per_mwh(Money.pln(Decimal(price2)))
    assert result == EnergyPrice.per_mwh(Money.pln(Decimal(expected)))


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("100.5", "50.25", "50.25"),
        ("0.0", "0.0", "0.0"),
        ("191.34", "67.89", "123.45"),
    ],
)
def test_sub(price1: str, price2: str, expected: str) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price1))) - EnergyPrice.per_mwh(Money.pln(Decimal(price2)))
    assert result == EnergyPrice.per_mwh(Money.pln(Decimal(expected)))


@pytest.mark.parametrize(
    ("price", "multiplier", "expected"),
    [
        ("100.0", "2", "200.0"),
        ("50.5", "0.5", "25.25"),
        ("0.0", "10", "0.0"),
    ],
)
def test_mul(price: str, multiplier: str, expected: str) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price))) * Decimal(multiplier)
    assert result == EnergyPrice.per_mwh(Money.pln(Decimal(expected)))


@pytest.mark.parametrize(
    ("price", "divisor", "expected"),
    [
        ("100.0", "2", "50.0"),
        ("50.5", "0.5", "101.0"),
        ("0.0", "10", "0.0"),
    ],
)
def test_div(price: str, divisor: str, expected: str) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price))) / Decimal(divisor)
    assert result == EnergyPrice.per_mwh(Money.pln(Decimal(expected)))


def test_div_by_zero() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        EnergyPrice.per_mwh(Money.pln(Decimal("100.0"))) / Decimal("0")  # pyright: ignore[reportUnusedExpression]


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("-10.0", "0.0", True),
        ("0.0", "0.0", False),
        ("100.0", "10.0", False),
    ],
)
def test_less_than(price1: str, price2: str, expected: bool) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price1))) < EnergyPrice.per_mwh(Money.pln(Decimal(price2)))
    assert result == expected


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("-10.0", "0.0", True),
        ("0.0", "0.0", True),
        ("100.0", "10.0", False),
    ],
)
def test_less_than_or_equal(price1: str, price2: str, expected: bool) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price1))) <= EnergyPrice.per_mwh(Money.pln(Decimal(price2)))
    assert result == expected


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("0.0", "-10.0", True),
        ("0.0", "0.0", False),
        ("10.0", "100.0", False),
    ],
)
def test_greater_than(price1: str, price2: str, expected: bool) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price1))) > EnergyPrice.per_mwh(Money.pln(Decimal(price2)))
    assert result == expected


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("0.0", "-10.0", True),
        ("0.0", "0.0", True),
        ("10.0", "100.0", False),
    ],
)
def test_greater_than_or_equal(price1: str, price2: str, expected: bool) -> None:
    result = EnergyPrice.per_mwh(Money.pln(Decimal(price1))) >= EnergyPrice.per_mwh(Money.pln(Decimal(price2)))
    assert result == expected


@pytest.mark.parametrize(
    "operation",
    [
        lambda a, b: a + b,
        lambda a, b: a - b,
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ],
)
def test_operation_with_different_unit(
    operation: Callable[[EnergyPrice, EnergyPrice], EnergyPrice | bool],
) -> None:
    price1 = EnergyPrice(Money(Decimal("100"), "PLN"), "MWh")
    price2 = EnergyPrice(Money(Decimal("50"), "PLN"), "kWh")
    with pytest.raises(ValueError, match="different unit"):
        operation(price1, price2)


def test_str() -> None:
    price = EnergyPrice.per_mwh(Money.pln(Decimal("123.4567")))
    assert format(price) == "123.46PLN/MWh"


@pytest.mark.parametrize(
    ("input_value", "expected_value"),
    [
        ("50.0", "50.0"),
        ("0.0", "0.0"),
        ("-25.0", "0.0"),
    ],
)
def test_non_negative(input_value: str, expected_value: str) -> None:
    price = EnergyPrice.per_mwh(Money.pln(Decimal(input_value)))
    expected = EnergyPrice.per_mwh(Money.pln(Decimal(expected_value)))
    assert price.non_negative() == expected
