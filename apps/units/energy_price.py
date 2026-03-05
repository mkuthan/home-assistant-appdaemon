from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar

from units.money import Money


@dataclass(frozen=True)
class EnergyPrice:
    _UNIT_KWH: ClassVar[str] = "kWh"
    _UNIT_MWH: ClassVar[str] = "MWh"

    money: Money
    unit: str

    def __post_init__(self) -> None:
        if self.unit not in [self._UNIT_KWH, self._UNIT_MWH]:
            raise ValueError(f"Unsupported unit {self.unit}")

    @property
    def value(self) -> Decimal:
        return self.money.value

    @property
    def currency(self) -> str:
        return self.money.currency

    def _check_compatible(self, other: "EnergyPrice", operation: str) -> None:
        if self.currency != other.currency or self.unit != other.unit:
            raise ValueError(f"Cannot {operation} energy prices with different currency or unit")

    def __add__(self, other: "EnergyPrice") -> "EnergyPrice":
        self._check_compatible(other, "add")
        return EnergyPrice(money=self.money + other.money, unit=self.unit)

    def __sub__(self, other: "EnergyPrice") -> "EnergyPrice":
        self._check_compatible(other, "subtract")
        return EnergyPrice(money=self.money - other.money, unit=self.unit)

    def __mul__(self, other: Decimal) -> "EnergyPrice":
        return EnergyPrice(money=self.money * other, unit=self.unit)

    def __truediv__(self, other: Decimal) -> "EnergyPrice":
        if other == Decimal(0):
            raise ValueError("Cannot divide by zero")
        return EnergyPrice(money=self.money / other, unit=self.unit)

    def __lt__(self, other: "EnergyPrice") -> bool:
        self._check_compatible(other, "compare")
        return self.money < other.money

    def __le__(self, other: "EnergyPrice") -> bool:
        self._check_compatible(other, "compare")
        return self.money <= other.money

    def __gt__(self, other: "EnergyPrice") -> bool:
        self._check_compatible(other, "compare")
        return self.money > other.money

    def __ge__(self, other: "EnergyPrice") -> bool:
        self._check_compatible(other, "compare")
        return self.money >= other.money

    def __str__(self) -> str:
        return f"{self.money}/{self.unit}"

    def non_negative(self) -> "EnergyPrice":
        return EnergyPrice(money=self.money.non_negative(), unit=self.unit)

    @classmethod
    def eur_per_kwh(cls, value: Decimal) -> "EnergyPrice":
        return cls(money=Money.eur(value), unit=cls._UNIT_KWH)

    @classmethod
    def eur_per_mwh(cls, value: Decimal) -> "EnergyPrice":
        return cls(money=Money.eur(value), unit=cls._UNIT_MWH)

    @classmethod
    def pln_per_kwh(cls, value: Decimal) -> "EnergyPrice":
        return cls(money=Money.pln(value), unit=cls._UNIT_KWH)

    @classmethod
    def pln_per_mwh(cls, value: Decimal) -> "EnergyPrice":
        return cls(money=Money.pln(value), unit=cls._UNIT_MWH)
