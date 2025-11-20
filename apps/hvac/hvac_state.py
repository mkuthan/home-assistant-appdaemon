from dataclasses import dataclass

from units.celsius import Celsius


@dataclass(frozen=True)
class HvacState:
    is_eco_mode: bool
    dhw_actual_temperature: Celsius
    dhw_target_temperature: Celsius
    indoor_actual_temperature: Celsius
    heating_target_temperature: Celsius
    heating_mode: str
    cooling_target_temperature: Celsius
    cooling_mode: str
    temperature_adjustment: Celsius
