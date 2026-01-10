import logging
from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from entities.entities import is_heating_enabled
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import Celsius
from utils.time_utils import is_time_in_range


class HeatingEstimator:
    _HEATING_CURVE_OFFSET_HIGH = Celsius(10.0)
    _HEATING_CURVE_OFFSET_LOW = Celsius(5.0)
    _HEATING_TARGET_OFFSET = Celsius(1.0)

    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: HvacConfiguration,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration

    def estimate_temperature(self, state: HvacState, now: datetime) -> Celsius | None:
        if not is_heating_enabled(state.heating_mode):
            return None

        if state.is_eco_mode:
            temperature_target = self.configuration.heating_temp_eco_on
            heating_boost_start = self.configuration.heating_boost_time_start_eco_on
            heating_boost_end = self.configuration.heating_boost_time_end_eco_on
        else:
            temperature_target = self.configuration.heating_temp_eco_off
            heating_boost_start = self.configuration.heating_boost_time_start_eco_off
            heating_boost_end = self.configuration.heating_boost_time_end_eco_off

        in_boost_window = is_time_in_range(now.time(), heating_boost_start, heating_boost_end)

        if in_boost_window:
            temperature_target += self._HEATING_TARGET_OFFSET

        temperature_target += state.temperature_adjustment

        temperature_target = round(temperature_target)

        if temperature_target != state.heating_target_temperature:
            self.appdaemon_logger.log(
                "Heating temperature target: %s, adjustment: %s",
                temperature_target,
                state.temperature_adjustment,
            )
            return temperature_target
        else:
            self.appdaemon_logger.log(
                "Heating temperature target unchanged: %s", temperature_target, level=logging.DEBUG
            )
            return None

    def estimate_curve_high_temperature(self, state: HvacState) -> Celsius | None:
        if not is_heating_enabled(state.heating_mode):
            return None

        if state.is_eco_mode:
            temperature_target = self.configuration.heating_temp_eco_on
        else:
            temperature_target = self.configuration.heating_temp_eco_off

        temperature_high = temperature_target + self._HEATING_CURVE_OFFSET_HIGH

        if temperature_high != state.heating_curve_target_high_temp:
            self.appdaemon_logger.log("Heating curve target high temperature: %s", temperature_high)
            return temperature_high
        else:
            self.appdaemon_logger.log(
                "Heating curve target high temperature unchanged: %s", temperature_high, level=logging.DEBUG
            )
            return None

    def estimate_curve_low_temperature(self, state: HvacState) -> Celsius | None:
        if not is_heating_enabled(state.heating_mode):
            return None

        if state.is_eco_mode:
            temperature_target = self.configuration.heating_temp_eco_on
        else:
            temperature_target = self.configuration.heating_temp_eco_off

        temperature_low = temperature_target + self._HEATING_CURVE_OFFSET_LOW

        if temperature_low != state.heating_curve_target_low_temp:
            self.appdaemon_logger.log("Heating curve target low temperature: %s", temperature_low)
            return temperature_low
        else:
            self.appdaemon_logger.log(
                "Heating curve target low temperature unchanged: %s", temperature_low, level=logging.DEBUG
            )
            return None
