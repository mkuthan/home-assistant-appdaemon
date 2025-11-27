from dataclasses import dataclass

from units.celsius import Celsius


@dataclass(frozen=True)
class HvacState:
    is_eco_mode: bool  # eco mode status
    dhw_actual_temperature: Celsius  # actual domestic hot water temperature
    dhw_target_temperature: Celsius  # target domestic hot water temperature
    indoor_actual_temperature: Celsius  # actual indoor temperature
    heating_target_temperature: Celsius  # target heating temperature
    heating_mode: str  # heating mode
    cooling_target_temperature: Celsius  # target cooling temperature
    cooling_mode: str  # cooling mode
    temperature_adjustment: Celsius  # temperature adjustment
