from dataclasses import dataclass

from units.celsius import Celsius


@dataclass(frozen=True)
class HvacState:
    is_eco_mode: bool
    dhw_temperature: Celsius
    heating_temperature: Celsius
    heating_mode: str
    cooling_temperature: Celsius
    cooling_mode: str
    temperature_adjustment: Celsius
