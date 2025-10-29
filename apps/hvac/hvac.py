from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from hvac.dhw_estimator import DhwEstimator
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from hvac.hvac_state_factory import HvacStateFactory
from units.celsius import Celsius


class Hvac:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        appdaemon_service: AppdaemonService,
        configuration: HvacConfiguration,
        state_factory: HvacStateFactory,
        dhw_estimator: DhwEstimator,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_service = appdaemon_service
        self.config = configuration
        self.state_factory = state_factory
        self.dhw_estimator = dhw_estimator

    def control(self, now: datetime) -> None:
        state = self.state_factory.create()
        if state is None:
            self.appdaemon_logger.warn("Unknown state, cannot control HVAC")
            return

        dhw_temperature = self.dhw_estimator.estimate_temperature(state, now)
        self._set_dhw_temperature(state, dhw_temperature)

    def _set_dhw_temperature(self, state: HvacState, temperature: Celsius) -> None:
        current_dhw_temperature = state.dhw_temperature
        if current_dhw_temperature != temperature:
            self.appdaemon_logger.info(f"Change DHW temperature from {current_dhw_temperature} to {temperature}")
            self.appdaemon_service.call_service(
                "water_heater.set_temperature",
                callback=self.appdaemon_service.service_call_callback,
                entity_id="water_heater.panasonic_heat_pump_main_dhw_target_temp",
                value=temperature.value,
            )
        else:
            self.appdaemon_logger.info(f"DHW temperature already set to {current_dhw_temperature}")
