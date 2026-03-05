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

    def __add__(self, other: "EnergyPrice") -> "EnergyPrice":
        if self.unit != other.unit:
            raise ValueError("Cannot add energy prices with different unit")
        return EnergyPrice(money=self.money + other.money, unit=self.unit)

    def __sub__(self, other: "EnergyPrice") -> "EnergyPrice":
        if self.unit != other.unit:
            raise ValueError("Cannot subtract energy prices with different unit")
        return EnergyPrice(money=self.money - other.money, unit=self.unit)

    def __mul__(self, other: Decimal) -> "EnergyPrice":
        return EnergyPrice(money=self.money * other, unit=self.unit)

    def __truediv__(self, other: Decimal) -> "EnergyPrice":
        if other == Decimal(0):
            raise ValueError("Cannot divide by zero")
        return EnergyPrice(money=self.money / other, unit=self.unit)

    def __lt__(self, other: "EnergyPrice") -> bool:
        if self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different unit")
        return self.money < other.money

    def __le__(self, other: "EnergyPrice") -> bool:
        if self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different unit")
        return self.money <= other.money

    def __gt__(self, other: "EnergyPrice") -> bool:
        if self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different unit")
        return self.money > other.money

    def __ge__(self, other: "EnergyPrice") -> bool:
        if self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different unit")
        return self.money >= other.money

    def __str__(self) -> str:
        return f"{self.money}/{self.unit}"

    def non_negative(self) -> "EnergyPrice":
        return EnergyPrice(money=self.money.non_negative(), unit=self.unit)

    @classmethod
    def per_kwh(cls, money: Money) -> "EnergyPrice":
        return cls(money=money, unit=cls._UNIT_KWH)

    @classmethod
    def per_mwh(cls, money: Money) -> "EnergyPrice":
        return cls(money=money, unit=cls._UNIT_MWH)
