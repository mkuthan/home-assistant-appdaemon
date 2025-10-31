from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from entities.entities import COOLING_ENTITY, DHW_ENTITY, HEATING_ENTITY
from hvac.cooling_estimator import CoolingEstimator
from hvac.dhw_estimator import DhwEstimator
from hvac.heating_estimator import HeatingEstimator
from hvac.hvac_configuration import HvacConfiguration
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
        heating_estimator: HeatingEstimator,
        cooling_estimator: CoolingEstimator,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_service = appdaemon_service
        self.config = configuration
        self.state_factory = state_factory
        self.dhw_estimator = dhw_estimator
        self.heating_estimator = heating_estimator
        self.cooling_estimator = cooling_estimator

    def control(self, now: datetime) -> None:
        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.warn("Unknown state, cannot control HVAC")
            return

        if (dhw_temperature := self.dhw_estimator.estimate_temperature(state, now)) is not None:
            self.appdaemon_logger.info(f"Change DHW temperature from {state.dhw_temperature} to {dhw_temperature}")
            self._set_dhw_temperature(dhw_temperature)

        if (heating_temperature := self.heating_estimator.estimate_temperature(state, now)) is not None:
            self.appdaemon_logger.info(
                f"Change heating temperature from {state.heating_temperature} to {heating_temperature}"
            )
            self._set_heating_temperature(heating_temperature)

        if (cooling_temperature := self.cooling_estimator.estimate_temperature(state, now)) is not None:
            self.appdaemon_logger.info(
                f"Change cooling temperature from {state.cooling_temperature} to {cooling_temperature}"
            )
            self._set_cooling_temperature(cooling_temperature)

    def _set_dhw_temperature(self, temperature: Celsius) -> None:
        self.appdaemon_service.call_service(
            "water_heater/set_temperature",
            callback=self.appdaemon_service.service_call_callback,
            entity_id=DHW_ENTITY,
            temperature=temperature.value,
        )

    def _set_heating_temperature(self, temperature: Celsius) -> None:
        self.appdaemon_service.call_service(
            "climate/set_temperature",
            callback=self.appdaemon_service.service_call_callback,
            entity_id=HEATING_ENTITY,
            temperature=temperature.value,
        )

    def _set_cooling_temperature(self, temperature: Celsius) -> None:
        self.appdaemon_service.call_service(
            "climate/set_temperature",
            callback=self.appdaemon_service.service_call_callback,
            entity_id=COOLING_ENTITY,
            temperature=temperature.value,
        )
