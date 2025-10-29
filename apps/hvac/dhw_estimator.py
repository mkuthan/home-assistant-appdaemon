from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import CELSIUS_ZERO, Celsius


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

        if self.configuration.dhw_boost_start <= now.time() <= self.configuration.dhw_boost_end:
            temperature_target += temperature_boost
        else:
            temperature_boost = CELSIUS_ZERO

        if temperature_target != state.dhw_temperature:
            self.appdaemon_logger.info(f"DHW temperature target: {temperature_target}, boost: {temperature_boost}")
            return temperature_target
        else:
            return None
