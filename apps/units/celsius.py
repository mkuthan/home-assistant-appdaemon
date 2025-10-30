from dataclasses import dataclass
from math import floor
from typing import ClassVar


@dataclass(frozen=True, order=True)
class Celsius:
    _ZERO_VALUE: ClassVar[float] = 0.0

    value: float

    def __add__(self, other: "Celsius") -> "Celsius":
        return Celsius(value=self.value + other.value)

    def __sub__(self, other: "Celsius") -> "Celsius":
        return Celsius(value=self.value - other.value)

    def __round__(self) -> "Celsius":
        return Celsius(value=floor(self.value + 0.5))

    def __str__(self) -> str:
        return f"{self.value:.1f}°C"


CELSIUS_ZERO = Celsius(Celsius._ZERO_VALUE)
