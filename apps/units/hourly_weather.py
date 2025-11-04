from dataclasses import dataclass

from units.celsius import Celsius
from units.hourly_period import HourlyPeriod


@dataclass(frozen=True)
class HourlyWeather:
    period: HourlyPeriod
    temperature: Celsius
    humidity: float

    def __str__(self) -> str:
        return f"{self.period} {self.temperature} {self.humidity}%"
