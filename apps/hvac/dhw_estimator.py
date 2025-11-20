from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import CELSIUS_ZERO, Celsius
from utils.time_utils import is_time_in_range


class DhwEstimator:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: HvacConfiguration,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration

    def estimate_temperature(self, state: HvacState, now: datetime) -> Celsius | None:
        if state.is_eco_mode:
            temperature_target = self.configuration.dhw_temp_eco
            temperature_boost = self.configuration.dhw_boost_delta_temp_eco
        else:
            temperature_target = self.configuration.dhw_temp
            temperature_boost = self.configuration.dhw_boost_delta_temp

        in_boost_period = is_time_in_range(
            now.time(), self.configuration.dhw_boost_start, self.configuration.dhw_boost_end
        )

        if in_boost_period:
            temperature_target += temperature_boost
        else:
            temperature_boost = CELSIUS_ZERO

        temperature_target = round(temperature_target)

        if temperature_target != state.dhw_target_temperature:
            self.appdaemon_logger.log("DHW temperature target: %s, boost: %s", temperature_target, temperature_boost)
            return temperature_target
        else:
            return None
