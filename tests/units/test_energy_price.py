from collections.abc import Callable
from decimal import Decimal

import pytest
from units.energy_price import EnergyPrice


@pytest.mark.parametrize(
    "price_value",
    [
        "-100.0",
        "-0.5",
        "0.0",
        "0.5",
        "100",
    ],
)
@pytest.mark.parametrize(
    ("callable", "currency", "unit"),
    [
        (EnergyPrice.pln_per_mwh, "PLN", "MWh"),
        (EnergyPrice.pln_per_kwh, "PLN", "kWh"),
        (EnergyPrice.eur_per_mwh, "EUR", "MWh"),
        (EnergyPrice.eur_per_kwh, "EUR", "kWh"),
    ],
)
def test_class_factory_method(
    price_value: str, callable: Callable[[Decimal], EnergyPrice], currency: str, unit: str
) -> None:
    price_decimal = Decimal(price_value)
    price = callable(price_decimal)
    assert price.value == price_decimal
    assert price.currency == currency
    assert price.unit == unit


@pytest.mark.parametrize(
    "currency",
    [
        "ABC",
        "XYZ",
    ],
)
def test_invalid_currency(currency: str) -> None:
    with pytest.raises(ValueError, match=f"Unsupported currency {currency}"):
        EnergyPrice(value=Decimal(0), currency=currency, unit="MWh")


@pytest.mark.parametrize(
    "unit",
    [
        "ABC",
        "XYZ",
    ],
)
def test_invalid_unit(unit: str) -> None:
    with pytest.raises(ValueError, match=f"Unsupported unit {unit}"):
        EnergyPrice(value=Decimal(0), currency="PLN", unit=unit)


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("100.5", "50.25", "150.75"),
        ("0.0", "0.0", "0.0"),
        ("123.45", "67.89", "191.34"),
    ],
)
def test_add(price1: str, price2: str, expected: str) -> None:
    result = EnergyPrice.pln_per_mwh(Decimal(price1)) + EnergyPrice.pln_per_mwh(Decimal(price2))
    assert result == EnergyPrice.pln_per_mwh(Decimal(expected))


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("100.5", "50.25", "50.25"),
        ("0.0", "0.0", "0.0"),
        ("191.34", "67.89", "123.45"),
    ],
)
def test_sub(price1: str, price2: str, expected: str) -> None:
    result = EnergyPrice.pln_per_mwh(Decimal(price1)) - EnergyPrice.pln_per_mwh(Decimal(price2))
    assert result == EnergyPrice.pln_per_mwh(Decimal(expected))


@pytest.mark.parametrize(
    ("price", "multiplier", "expected"),
    [
        ("100.0", "2", "200.0"),
        ("50.5", "0.5", "25.25"),
        ("0.0", "10", "0.0"),
    ],
)
def test_mul(price: str, multiplier: str, expected: str) -> None:
    result = EnergyPrice.pln_per_mwh(Decimal(price)) * Decimal(multiplier)
    assert result == EnergyPrice.pln_per_mwh(Decimal(expected))


@pytest.mark.parametrize(
    ("price", "divisor", "expected"),
    [
        ("100.0", "2", "50.0"),
        ("50.5", "0.5", "101.0"),
        ("0.0", "10", "0.0"),
    ],
)
def test_div(price: str, divisor: str, expected: str) -> None:
    result = EnergyPrice.pln_per_mwh(Decimal(price)) / Decimal(divisor)
    assert result == EnergyPrice.pln_per_mwh(Decimal(expected))


def test_div_by_zero() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        EnergyPrice.pln_per_mwh(Decimal("100.0")) / Decimal("0")  # pyright: ignore[reportUnusedExpression]


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        ("-10.0", "0.0", True),
        ("0.0", "0.0", False),
        ("100.0", "10.0", False),
    ],
)
def test_less_than(price1: str, price2: str, expected: bool) -> None:
    result = EnergyPrice.pln_per_mwh(Decimal(price1)) < EnergyPrice.pln_per_mwh(Decimal(price2))
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
    result = EnergyPrice.pln_per_mwh(Decimal(price1)) <= EnergyPrice.pln_per_mwh(Decimal(price2))
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
    result = EnergyPrice.pln_per_mwh(Decimal(price1)) > EnergyPrice.pln_per_mwh(Decimal(price2))
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
    result = EnergyPrice.pln_per_mwh(Decimal(price1)) >= EnergyPrice.pln_per_mwh(Decimal(price2))
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
@pytest.mark.parametrize(
    "price1,price2",
    [
        (EnergyPrice(Decimal("100"), "PLN", "MWh"), EnergyPrice(Decimal("50"), "EUR", "MWh")),
        (EnergyPrice(Decimal("100"), "PLN", "MWh"), EnergyPrice(Decimal("50"), "PLN", "kWh")),
    ],
)
def test_operation_with_incompatible_prices(
    operation: Callable[[EnergyPrice, EnergyPrice], EnergyPrice | bool],
    price1: EnergyPrice,
    price2: EnergyPrice,
) -> None:
    with pytest.raises(ValueError, match="with different currency or unit"):
        operation(price1, price2)


def test_str() -> None:
    price = EnergyPrice.pln_per_mwh(Decimal("123.4567"))
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
    price = EnergyPrice.pln_per_mwh(Decimal(input_value))
    expected = EnergyPrice.pln_per_mwh(Decimal(expected_value))
    assert price.non_negative() == expected


def test_zeroed() -> None:
    price = EnergyPrice.pln_per_mwh(Decimal("123.45"))
    expected = EnergyPrice.pln_per_mwh(Decimal("0.0"))
    assert price.zeroed() == expected
