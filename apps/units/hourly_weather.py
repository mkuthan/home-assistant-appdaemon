from dataclasses import dataclass

from units.hourly_period import HourlyPeriod


@dataclass(frozen=True)
class HourlyWeather:
    period: HourlyPeriod
    temperature: float
    humidity: float

    def __str__(self) -> str:
        return f"{self.period} {self.temperature}C {self.humidity}%"
