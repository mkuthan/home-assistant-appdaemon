from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class EnergyPrice:
    _CURRENCY_PLN: ClassVar[str] = "PLN"
    _UNIT_MWH: ClassVar[str] = "MWh"

    value: float
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
            raise ValueError("Cannot substract energy prices with different currency or unit")

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnergyPrice):
            return NotImplemented
        return self.value == other.value and self.currency == other.currency and self.unit == other.unit

    def __format__(self, _format_spec: str) -> str:
        return f"{self.value:.2f} {self.currency}/{self.unit}"

    def max_with_zero(self) -> "EnergyPrice":
        return EnergyPrice(value=max(0.0, self.value), currency=self.currency, unit=self.unit)

    @staticmethod
    def pln_per_mwh(value: float) -> "EnergyPrice":
        return EnergyPrice(value=value, currency=EnergyPrice._CURRENCY_PLN, unit=EnergyPrice._UNIT_MWH)
