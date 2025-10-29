from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import Celsius


class DhwEstimator:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: HvacConfiguration,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration

    def estimate_temperature(self, state: HvacState, now: datetime) -> Celsius:
        if state.is_eco_mode:
            temperature_target = self.configuration.dhw_temp_eco
            temperature_boost = self.configuration.dhw_boost_delta_temp_eco
        else:
            temperature_target = self.configuration.dhw_temp
            temperature_boost = self.configuration.dhw_boost_delta_temp

        if self.configuration.dhw_boost_start <= now.time() <= self.configuration.dhw_boost_end:
            temperature_target += temperature_boost
            self.appdaemon_logger.info(f"Boost DHW temperature by {temperature_boost} to {temperature_target}")
            return temperature_target

        return temperature_target
