import logging
from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from appdaemon_protocols.appdaemon_state import AppdaemonState
from entities.entities import COOLING_ENTITY, DHW_ENTITY, ECO_MODE_ENTITY, HEATING_ENTITY, TEMPERATURE_ADJUSTMENT_ENTITY
from hvac.hvac_state import HvacState
from units.celsius import Celsius
from utils.safe_converters import safe_bool, safe_float, safe_str


class HvacStateFactory(Protocol):
    def create(self) -> HvacState | None: ...


class DefaultHvacStateFactory:
    def __init__(
        self, appdaemon_logger: AppdaemonLogger, appdaemon_state: AppdaemonState, appdaemon_service: AppdaemonService
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_state = appdaemon_state
        self.appdaemon_service = appdaemon_service

    def create(self) -> HvacState | None:
        is_eco_mode = safe_bool(self.appdaemon_state.get_state(ECO_MODE_ENTITY))
        dhw_temperature = safe_float(self.appdaemon_state.get_state(DHW_ENTITY, "temperature"))
        heating_temperature = safe_float(self.appdaemon_state.get_state(HEATING_ENTITY, "temperature"))
        heating_mode = safe_str(self.appdaemon_state.get_state(HEATING_ENTITY))
        cooling_temperature = safe_float(self.appdaemon_state.get_state(COOLING_ENTITY, "temperature"))
        cooling_mode = safe_str(self.appdaemon_state.get_state(COOLING_ENTITY))
        temperature_adjustment = safe_float(self.appdaemon_state.get_state(TEMPERATURE_ADJUSTMENT_ENTITY))

        missing = [
            name
            for name, value in [
                ("is_eco_mode", is_eco_mode),
                ("dhw_temperature", dhw_temperature),
                ("heating_temperature", heating_temperature),
                ("heating_mode", heating_mode),
                ("cooling_temperature", cooling_temperature),
                ("cooling_mode", cooling_mode),
                ("temperature_adjustment", temperature_adjustment),
            ]
            if value is None
        ]

        if missing:
            self.appdaemon_logger.log(f"Missing: {', '.join(missing)}", level=logging.WARNING)
            return None

        assert is_eco_mode is not None
        assert dhw_temperature is not None
        assert heating_temperature is not None
        assert heating_mode is not None
        assert cooling_temperature is not None
        assert cooling_mode is not None
        assert temperature_adjustment is not None

        return HvacState(
            is_eco_mode=is_eco_mode,
            dhw_temperature=Celsius(dhw_temperature),
            heating_temperature=Celsius(heating_temperature),
            heating_mode=heating_mode,
            cooling_temperature=Celsius(cooling_temperature),
            cooling_mode=cooling_mode,
            temperature_adjustment=Celsius(temperature_adjustment),
        )
