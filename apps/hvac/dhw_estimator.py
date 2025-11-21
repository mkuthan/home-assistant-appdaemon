from datetime import datetime, timedelta

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import CELSIUS_ZERO, Celsius
from utils.time_utils import is_time_in_range


class DhwEstimator:
    _BOOST_LEAD_TIME_HOURS = 1

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
        else:
            temperature_target = self.configuration.dhw_temp

        in_boost_window = is_time_in_range(
            now.time(), self.configuration.dhw_boost_start, self.configuration.dhw_boost_end
        )
        in_boost_start_window = is_time_in_range(
            (now + timedelta(hours=self._BOOST_LEAD_TIME_HOURS)).time(),
            self.configuration.dhw_boost_start,
            self.configuration.dhw_boost_end,
        )

        needs_temperature_boost = temperature_target - state.dhw_actual_temperature >= self.configuration.dhw_delta_temp

        is_boost_active = state.dhw_target_temperature > temperature_target

        should_apply_boost = is_boost_active or (needs_temperature_boost and in_boost_start_window)

        if in_boost_window and should_apply_boost:
            temperature_boost = self.configuration.dhw_delta_temp
            temperature_target += temperature_boost
        else:
            temperature_boost = CELSIUS_ZERO

        temperature_target = round(temperature_target)

        if temperature_target != state.dhw_target_temperature:
            self.appdaemon_logger.log("DHW temperature target: %s, boost: %s", temperature_target, temperature_boost)
            return temperature_target
        else:
            return None
