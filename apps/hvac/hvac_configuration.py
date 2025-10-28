from dataclasses import dataclass
from datetime import time

from units.celsius import Celsius


@dataclass(frozen=True)
class HvacConfiguration:
    dhw_temp: Celsius  # domestic hot water temperature setpoint
    dhw_temp_eco: Celsius  # domestic hot water temperature setpoint in eco mode
    dhw_boost_delta_temp: Celsius
    dhw_boost_delta_temp_eco: Celsius
    dhw_boost_start: time
    dhw_boost_end: time

    heating_temp: Celsius  # heating temperature setpoint
    heating_temp_eco: Celsius  # heating temperature setpoint in eco mode
    heating_boost_delta_temp: Celsius
    heating_boost_delta_temp_eco: Celsius
    heating_boost_time_start_eco_on: time
    heating_boost_time_end_eco_on: time
    heating_boost_time_start_eco_off: time
    heating_boost_time_end_eco_off: time

    cooling_temp: Celsius  # cooling temperature setpoint
    cooling_temp_eco: Celsius  # cooling temperature setpoint in eco mode
    cooling_reduced_delta_temp: Celsius
    cooling_reduced_delta_temp_eco: Celsius
    cooling_reduced_time_start_eco_on: time
    cooling_reduced_time_end_eco_on: time
    cooling_reduced_time_start_eco_off: time
    cooling_reduced_time_end_eco_off: time
