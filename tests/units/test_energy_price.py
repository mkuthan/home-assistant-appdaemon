from decimal import Decimal

import pytest
from units.energy_price import ENERGY_PRICE_ZERO, EnergyPrice


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
def test_pln_per_mwh(price_value: str) -> None:
    price_decimal = Decimal(price_value)
    price = EnergyPrice.pln_per_mwh(price_decimal)
    assert price.value == price_decimal
    assert price.currency == "PLN"
    assert price.unit == "MWh"


@pytest.mark.parametrize(
    "currency",
    [
        "USD",
        "EUR",
        "GBP",
    ],
)
def test_invalid_currency(currency: str) -> None:
    with pytest.raises(ValueError, match=f"Unsupported currency, expected PLN, got {currency}"):
        EnergyPrice(value=Decimal(0), currency=currency, unit="MWh")


@pytest.mark.parametrize(
    "unit",
    [
        "kWh",
        "GWh",
        "Wh",
    ],
)
def test_invalid_unit(unit: str) -> None:
    with pytest.raises(ValueError, match=f"Unsupported unit, expected MWh, got {unit}"):
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
    ("price_value", "expected_value"),
    [
        ("-10.0", "0.0"),
        ("0.0", "0.0"),
        ("10.0", "10.0"),
    ],
)
def test_max(price_value: str, expected_value: str) -> None:
    price = EnergyPrice.pln_per_mwh(Decimal(price_value))
    expected = EnergyPrice.pln_per_mwh(Decimal(expected_value))
    # max uses __lt__, __le__, __gt__, __ge__ methods
    assert max(price, ENERGY_PRICE_ZERO) == expected


def test_str() -> None:
    price = EnergyPrice.pln_per_mwh(Decimal("123.4567"))
    assert format(price) == "123.46PLN/MWh"
