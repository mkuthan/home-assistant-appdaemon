from decimal import Decimal

import pytest
from units.energy_price import EnergyPrice


@pytest.mark.parametrize(
    "price_value",
    [
        -100.0,
        -0.5,
        0.0,
        0.5,
        100,
    ],
)
def test_pln_per_mwh(price_value: float) -> None:
    price = EnergyPrice.pln_per_mwh(price_value)
    assert price.value == price_value
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
        EnergyPrice(value=100.0, currency=currency, unit="MWh")


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
        EnergyPrice(value=100.0, currency="PLN", unit=unit)


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        (-10.0, 0.0, True),
        (0.0, 0.0, False),
        (100.0, 10.0, False),
    ],
)
def test_less_than(price1: float, price2: float, expected: bool) -> None:
    result = EnergyPrice.pln_per_mwh(price1) < EnergyPrice.pln_per_mwh(price2)
    assert result == expected


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        (-10.0, 0.0, True),
        (0.0, 0.0, True),
        (100.0, 10.0, False),
    ],
)
def test_less_than_or_equal(price1: float, price2: float, expected: bool) -> None:
    result = EnergyPrice.pln_per_mwh(price1) <= EnergyPrice.pln_per_mwh(price2)
    assert result == expected


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        (0.0, -10.0, True),
        (0.0, 0.0, False),
        (10.0, 100.0, False),
    ],
)
def test_greater_than(price1: float, price2: float, expected: bool) -> None:
    result = EnergyPrice.pln_per_mwh(price1) > EnergyPrice.pln_per_mwh(price2)
    assert result == expected


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        (0.0, -10.0, True),
        (0.0, 0.0, True),
        (10.0, 100.0, False),
    ],
)
def test_greater_than_or_equal(price1: float, price2: float, expected: bool) -> None:
    result = EnergyPrice.pln_per_mwh(price1) >= EnergyPrice.pln_per_mwh(price2)
    assert result == expected


def test_str() -> None:
    price = EnergyPrice.pln_per_mwh(123.4567)
    assert format(price) == "123.46PLN/MWh"


@pytest.mark.parametrize(
    ("price_value", "expected_value"),
    [
        (-10.0, 0.0),
        (0.0, 0.0),
        (10.0, 10.0),
    ],
)
def test_max_with_zero(price_value: float, expected_value: float) -> None:
    price = EnergyPrice.pln_per_mwh(price_value)
    expected = EnergyPrice.pln_per_mwh(expected_value)
    assert price.max_with_zero() == expected


def test_pln_per_mwh_converts_float_to_decimal() -> None:
    price = EnergyPrice.pln_per_mwh(123.45)
    assert price.value == Decimal("123.45")


def test_pln_per_mwh_accepts_decimal() -> None:
    price = EnergyPrice.pln_per_mwh(Decimal("99.99"))
    assert price.value == Decimal("99.99")


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        (100.5, 50.25, 150.75),
        (0.0, 0.0, 0.0),
        (123.45, 67.89, 191.34),
    ],
)
def test_add(price1: float, price2: float, expected: float) -> None:
    result = EnergyPrice.pln_per_mwh(price1) + EnergyPrice.pln_per_mwh(price2)
    assert result == EnergyPrice.pln_per_mwh(expected)


@pytest.mark.parametrize(
    ("price1", "price2", "expected"),
    [
        (100.5, 50.25, 50.25),
        (0.0, 0.0, 0.0),
        (191.34, 67.89, 123.45),
    ],
)
def test_sub(price1: float, price2: float, expected: float) -> None:
    result = EnergyPrice.pln_per_mwh(price1) - EnergyPrice.pln_per_mwh(price2)
    assert result == EnergyPrice.pln_per_mwh(expected)
