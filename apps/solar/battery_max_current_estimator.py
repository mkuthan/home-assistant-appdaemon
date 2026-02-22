import logging
from datetime import datetime, time

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.battery_discharge_slot import BatteryDischargeSlot
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_current import BatteryCurrent
from utils.time_utils import is_time_in_range


class BatteryMaxCurrentEstimator:
    _NIGHT_CHARGE_START = time(22, 0)
    _NIGHT_CHARGE_END = time(7, 0)

    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: SolarConfiguration,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration

    def estimate_battery_max_charge_current(self, state: SolarState, now: datetime) -> BatteryCurrent | None:
        if is_time_in_range(now.time(), self._NIGHT_CHARGE_START, self._NIGHT_CHARGE_END):
            target = self.configuration.battery_night_charge_current
        else:
            target = self.configuration.battery_nominal_current

        if target != state.battery_max_charge_current:
            self.appdaemon_logger.log("Battery max charge current target: %s", target)
            return target
        else:
            self.appdaemon_logger.log("Battery max charge current unchanged: %s", target, level=logging.DEBUG)
            return None

    def estimate_battery_max_discharge_current(self, state: SolarState, now: datetime) -> BatteryCurrent | None:
        if state.is_slot1_discharge_enabled and state.slot1_discharge_time:
            slot = BatteryDischargeSlot.from_time_str(
                state.slot1_discharge_time, self.configuration.battery_maximum_current
            )
            in_slot = is_time_in_range(now.time(), slot.start_time, slot.end_time)
        else:
            in_slot = False

        target = self.configuration.battery_maximum_current if in_slot else self.configuration.battery_nominal_current

        if target != state.battery_max_discharge_current:
            self.appdaemon_logger.log("Battery max discharge current target: %s", target)
            return target
        else:
            self.appdaemon_logger.log("Battery max discharge current unchanged: %s", target, level=logging.DEBUG)
            return None
