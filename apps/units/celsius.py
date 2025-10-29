from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, order=True)
class Celsius:
    _ZERO_VALUE: ClassVar[float] = 0.0

    value: float

    def __add__(self, other: "Celsius") -> "Celsius":
        return Celsius(value=self.value + other.value)

    def __sub__(self, other: "Celsius") -> "Celsius":
        return Celsius(value=self.value - other.value)

    def __str__(self) -> str:
        return f"{self.value:.1f}°C"


CELSIUS_ZERO = Celsius(Celsius._ZERO_VALUE)
