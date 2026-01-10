from dataclasses import dataclass
from datetime import time

from units.celsius import Celsius


@dataclass(frozen=True)
class HvacConfiguration:
    time_zone: str

    dhw_temp_eco_off: Celsius
    dhw_temp_eco_on: Celsius
    dhw_delta_temp_eco_off: Celsius
    dhw_delta_temp_eco_on: Celsius
    dhw_boost_start: time
    dhw_boost_end: time

    heating_temp_eco_off: Celsius
    heating_temp_eco_on: Celsius
    heating_boost_time_start_eco_on: time
    heating_boost_time_end_eco_on: time
    heating_boost_time_start_eco_off: time
    heating_boost_time_end_eco_off: time

    cooling_temp_eco_off: Celsius
    cooling_temp_eco_on: Celsius
    cooling_boost_time_start_eco_on: time
    cooling_boost_time_end_eco_on: time
    cooling_boost_time_start_eco_off: time
    cooling_boost_time_end_eco_off: time
