from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from entities.entities import is_heating_enabled
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import CELSIUS_ZERO, Celsius
from utils.time_utils import is_time_in_range


class HeatingEstimator:
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
            temperature_target = self.configuration.heating_temp_eco
            temperature_boost = self.configuration.heating_boost_delta_temp_eco
            heating_boost_start = self.configuration.heating_boost_time_start_eco_on
            heating_boost_end = self.configuration.heating_boost_time_end_eco_on
        else:
            temperature_target = self.configuration.heating_temp
            temperature_boost = self.configuration.heating_boost_delta_temp
            heating_boost_start = self.configuration.heating_boost_time_start_eco_off
            heating_boost_end = self.configuration.heating_boost_time_end_eco_off

        in_boost_period = is_time_in_range(now.time(), heating_boost_start, heating_boost_end)

        if in_boost_period:
            temperature_target += temperature_boost
        else:
            temperature_boost = CELSIUS_ZERO

        temperature_target = round(temperature_target)

        if temperature_target != state.heating_temperature:
            self.appdaemon_logger.info(f"Heating temperature target: {temperature_target}, boost: {temperature_boost}")
            return temperature_target
        else:
            return None
