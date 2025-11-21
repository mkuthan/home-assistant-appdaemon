from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from entities.entities import is_cooling_enabled
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import CELSIUS_ZERO, Celsius
from utils.time_utils import is_time_in_range


class CoolingEstimator:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: HvacConfiguration,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration

    def estimate_temperature(self, state: HvacState, now: datetime) -> Celsius | None:
        if not is_cooling_enabled(state.heating_mode):
            return None

        if state.is_eco_mode:
            temperature_target = self.configuration.cooling_temp_eco
            temperature_boost = self.configuration.cooling_boost_delta_temp_eco
            cooling_boost_start = self.configuration.cooling_boost_time_start_eco_on
            cooling_boost_end = self.configuration.cooling_boost_time_end_eco_on
        else:
            temperature_target = self.configuration.cooling_temp
            temperature_boost = self.configuration.cooling_boost_delta_temp
            cooling_boost_start = self.configuration.cooling_boost_time_start_eco_off
            cooling_boost_end = self.configuration.cooling_boost_time_end_eco_off

        in_boost_window = is_time_in_range(now.time(), cooling_boost_start, cooling_boost_end)

        if in_boost_window:
            temperature_target -= temperature_boost
        else:
            temperature_boost = CELSIUS_ZERO

        temperature_target += state.temperature_adjustment

        temperature_target = round(temperature_target)

        if temperature_target != state.cooling_target_temperature:
            self.appdaemon_logger.log(
                "Cooling temperature target: %s, boost: %s, adjustment: %s",
                temperature_target,
                temperature_boost,
                state.temperature_adjustment,
            )
            return temperature_target
        else:
            return None
