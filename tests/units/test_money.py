from collections.abc import Callable
from decimal import Decimal

import pytest
from units.money import Money


@pytest.mark.parametrize(
    "amount_value",
    [
        "-100.0",
        "-0.5",
        "0.0",
        "0.5",
        "100",
    ],
)
@pytest.mark.parametrize(
    ("callable", "currency"),
    [
        (Money.eur, "EUR"),
        (Money.pln, "PLN"),
    ],
)
def test_class_factory_method(amount_value: str, callable: Callable[[Decimal], Money], currency: str) -> None:
    amount_decimal = Decimal(amount_value)
    money = callable(amount_decimal)
    assert money.value == amount_decimal
    assert money.currency == currency


@pytest.mark.parametrize(
    "currency",
    [
        "ABC",
        "XYZ",
    ],
)
def test_invalid_currency(currency: str) -> None:
    with pytest.raises(ValueError, match=f"Unsupported currency {currency}"):
        Money(value=Decimal(0), currency=currency)


@pytest.mark.parametrize(
    ("amount1", "amount2", "expected"),
    [
        ("100.5", "50.25", "150.75"),
        ("0.0", "0.0", "0.0"),
        ("123.45", "67.89", "191.34"),
    ],
)
def test_add(amount1: str, amount2: str, expected: str) -> None:
    result = Money.pln(Decimal(amount1)) + Money.pln(Decimal(amount2))
    assert result == Money.pln(Decimal(expected))


@pytest.mark.parametrize(
    ("amount1", "amount2", "expected"),
    [
        ("100.5", "50.25", "50.25"),
        ("0.0", "0.0", "0.0"),
        ("191.34", "67.89", "123.45"),
    ],
)
def test_sub(amount1: str, amount2: str, expected: str) -> None:
    result = Money.pln(Decimal(amount1)) - Money.pln(Decimal(amount2))
    assert result == Money.pln(Decimal(expected))


@pytest.mark.parametrize(
    ("amount", "multiplier", "expected"),
    [
        ("100.0", "2", "200.0"),
        ("50.5", "0.5", "25.25"),
        ("0.0", "10", "0.0"),
    ],
)
def test_mul(amount: str, multiplier: str, expected: str) -> None:
    result = Money.pln(Decimal(amount)) * Decimal(multiplier)
    assert result == Money.pln(Decimal(expected))


@pytest.mark.parametrize(
    ("amount", "divisor", "expected"),
    [
        ("100.0", "2", "50.0"),
        ("50.5", "0.5", "101.0"),
        ("0.0", "10", "0.0"),
    ],
)
def test_div(amount: str, divisor: str, expected: str) -> None:
    result = Money.pln(Decimal(amount)) / Decimal(divisor)
    assert result == Money.pln(Decimal(expected))


def test_div_by_zero() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Money.pln(Decimal("100.0")) / Decimal("0")  # pyright: ignore[reportUnusedExpression]


@pytest.mark.parametrize(
    ("amount1", "amount2", "expected"),
    [
        ("-10.0", "0.0", True),
        ("0.0", "0.0", False),
        ("100.0", "10.0", False),
    ],
)
def test_less_than(amount1: str, amount2: str, expected: bool) -> None:
    result = Money.pln(Decimal(amount1)) < Money.pln(Decimal(amount2))
    assert result == expected


@pytest.mark.parametrize(
    ("amount1", "amount2", "expected"),
    [
        ("-10.0", "0.0", True),
        ("0.0", "0.0", True),
        ("100.0", "10.0", False),
    ],
)
def test_less_than_or_equal(amount1: str, amount2: str, expected: bool) -> None:
    result = Money.pln(Decimal(amount1)) <= Money.pln(Decimal(amount2))
    assert result == expected


@pytest.mark.parametrize(
    ("amount1", "amount2", "expected"),
    [
        ("0.0", "-10.0", True),
        ("0.0", "0.0", False),
        ("10.0", "100.0", False),
    ],
)
def test_greater_than(amount1: str, amount2: str, expected: bool) -> None:
    result = Money.pln(Decimal(amount1)) > Money.pln(Decimal(amount2))
    assert result == expected


@pytest.mark.parametrize(
    ("amount1", "amount2", "expected"),
    [
        ("0.0", "-10.0", True),
        ("0.0", "0.0", True),
        ("10.0", "100.0", False),
    ],
)
def test_greater_than_or_equal(amount1: str, amount2: str, expected: bool) -> None:
    result = Money.pln(Decimal(amount1)) >= Money.pln(Decimal(amount2))
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
def test_operation_with_incompatible_currencies(
    operation: Callable[[Money, Money], Money | bool],
) -> None:
    with pytest.raises(ValueError, match="with different currency"):
        operation(Money.pln(Decimal("100")), Money.eur(Decimal("50")))


def test_str() -> None:
    money = Money.pln(Decimal("123.4567"))
    assert format(money) == "123.46PLN"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        ("10.0", "10.0"),
        ("0.0", "0.0"),
        ("-5.0", "0.0"),
    ],
)
def test_non_negative(amount: str, expected: str) -> None:
    result = Money.pln(Decimal(amount)).non_negative()
    assert result == Money.pln(Decimal(expected))


def test_zeroed() -> None:
    result = Money.pln(Decimal("123.45")).zeroed()
    assert result == Money.pln(Decimal("0"))
