from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


@dataclass(frozen=True)
class EnergyPrice:
    _CURRENCY_PLN: ClassVar[str] = "PLN"
    _UNIT_MWH: ClassVar[str] = "MWh"

    value: Decimal
    currency: str
    unit: str

    def __post_init__(self) -> None:
        if self.currency != self._CURRENCY_PLN:
            raise ValueError(f"Unsupported currency, expected {self._CURRENCY_PLN}, got {self.currency}")
        if self.unit != self._UNIT_MWH:
            raise ValueError(f"Unsupported unit, expected {self._UNIT_MWH}, got {self.unit}")

    def __add__(self, other: "EnergyPrice") -> "EnergyPrice":
        if self.currency != other.currency or self.unit != other.unit:
            raise ValueError("Cannot add energy prices with different currency or unit")

        return EnergyPrice(value=self.value + other.value, currency=self.currency, unit=self.unit)

    def __sub__(self, other: "EnergyPrice") -> "EnergyPrice":
        if self.currency != other.currency or self.unit != other.unit:
            raise ValueError("Cannot subtract energy prices with different currency or unit")

        return EnergyPrice(value=self.value - other.value, currency=self.currency, unit=self.unit)

    def __lt__(self, other: "EnergyPrice") -> bool:
        if self.currency != other.currency or self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different currency or unit")
        return self.value < other.value

    def __le__(self, other: "EnergyPrice") -> bool:
        if self.currency != other.currency or self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different currency or unit")
        return self.value <= other.value

    def __gt__(self, other: "EnergyPrice") -> bool:
        if self.currency != other.currency or self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different currency or unit")
        return self.value > other.value

    def __ge__(self, other: "EnergyPrice") -> bool:
        if self.currency != other.currency or self.unit != other.unit:
            raise ValueError("Cannot compare energy prices with different currency or unit")
        return self.value >= other.value

    def __str__(self) -> str:
        return f"{self.value:.2f}{self.currency}/{self.unit}"

    @classmethod
    def pln_per_mwh(cls, value: Decimal) -> "EnergyPrice":
        return cls(value=value, currency=EnergyPrice._CURRENCY_PLN, unit=EnergyPrice._UNIT_MWH)


ENERGY_PRICE_ZERO = EnergyPrice.pln_per_mwh(Decimal(0))
