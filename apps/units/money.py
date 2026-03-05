from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


@dataclass(frozen=True)
class Money:
    _CURRENCY_EUR: ClassVar[str] = "EUR"
    _CURRENCY_PLN: ClassVar[str] = "PLN"

    value: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.currency not in [self._CURRENCY_EUR, self._CURRENCY_PLN]:
            raise ValueError(f"Unsupported currency {self.currency}")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currency")

        return Money(value=self.value + other.value, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currency")

        return Money(value=self.value - other.value, currency=self.currency)

    def __mul__(self, other: Decimal) -> "Money":
        return Money(value=self.value * other, currency=self.currency)

    def __truediv__(self, other: Decimal) -> "Money":
        if other == Decimal(0):
            raise ValueError("Cannot divide by zero")

        return Money(value=self.value / other, currency=self.currency)

    def __lt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currency")
        return self.value < other.value

    def __le__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currency")
        return self.value <= other.value

    def __gt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currency")
        return self.value > other.value

    def __ge__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currency")
        return self.value >= other.value

    def __str__(self) -> str:
        return f"{self.value:.2f}{self.currency}"

    def non_negative(self) -> "Money":
        return self if self.value >= Decimal(0) else Money(Decimal(0), self.currency)

    def zeroed(self) -> "Money":
        return Money(Decimal(0), self.currency)

    @classmethod
    def eur(cls, value: Decimal) -> "Money":
        return cls(value=value, currency=Money._CURRENCY_EUR)

    @classmethod
    def pln(cls, value: Decimal) -> "Money":
        return cls(value=value, currency=Money._CURRENCY_PLN)
