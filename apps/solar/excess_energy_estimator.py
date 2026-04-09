import logging
from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_soc import BatterySoc


class ExcessEnergyEstimator:
    _BATTERY_SOC_THRESHOLD = BatterySoc(90.0)

    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: SolarConfiguration,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration

    def estimate_excess_energy_mode(self, state: SolarState, now: datetime) -> bool | None:  # noqa: ARG002
        is_price_below_threshold = state.hourly_price < self.configuration.pv_export_threshold_price
        is_battery_soc_high = state.battery_soc > self._BATTERY_SOC_THRESHOLD

        is_excess_energy_mode_enabled = is_price_below_threshold and is_battery_soc_high

        if is_excess_energy_mode_enabled != state.is_excess_energy_mode_enabled:
            action = "Enable" if is_excess_energy_mode_enabled else "Disable"
            self.appdaemon_logger.log(
                "%s excess energy mode, price: %s, battery SoC: %s",
                action,
                state.hourly_price,
                state.battery_soc,
            )
            return is_excess_energy_mode_enabled
        else:
            self.appdaemon_logger.log("Excess energy mode: %s", is_excess_energy_mode_enabled, level=logging.DEBUG)
            return None
