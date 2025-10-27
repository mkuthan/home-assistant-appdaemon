from dataclasses import dataclass

from units.celsius import Celsius


@dataclass(frozen=True)
class HvacConfiguration:
    dhw_temp: Celsius  # domestic hot water temperature setpoint
    dhw_temp_eco: Celsius  # domestic hot water temperature setpoint in eco mode
    dhw_boost_delta_temp: Celsius  # domestic hot water boost temperature setpoint
    dhw_boost_delta_temp_eco: Celsius  # domestic hot water boost temperature setpoint in eco mode

    heating_temp: Celsius  # heating temperature setpoint
    heating_temp_eco: Celsius  # heating temperature setpoint in eco mode
    heating_reduced_delta_temp: Celsius  # heating reduced temperature setpoint
    heating_reduced_delta_temp_eco: Celsius  # heating reduced temperature setpoint in eco mode

    cooling_temp: Celsius  # cooling temperature setpoint
    cooling_temp_eco: Celsius  # cooling temperature setpoint in eco mode
    cooling_reduced_delta_temp: Celsius  # cooling reduced temperature setpoint
    cooling_reduced_delta_temp_eco: Celsius  # cooling reduced temperature setpoint in eco mode
