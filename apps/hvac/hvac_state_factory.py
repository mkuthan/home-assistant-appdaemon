import logging
from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_state import AppdaemonState
from entities.entities import (
    COOLING_ENTITY,
    DHW_DELTA_TEMP_ENTITY,
    DHW_ENTITY,
    DHW_TEMPERATURE_ENTITY,
    ECO_MODE_ENTITY,
    HEATING_CURVE_TARGET_HIGH_TEMP_ENTITY,
    HEATING_CURVE_TARGET_LOW_TEMP_ENTITY,
    HEATING_ENTITY,
    INDOOR_TEMPERATURE_ENTITY,
    TEMPERATURE_ADJUSTMENT_ENTITY,
)
from hvac.hvac_state import HvacState
from units.celsius import Celsius
from utils.safe_converters import safe_bool, safe_float, safe_str


class HvacStateFactory(Protocol):
    def create(self) -> HvacState | None: ...


class DefaultHvacStateFactory:
    def __init__(self, appdaemon_logger: AppdaemonLogger, appdaemon_state: AppdaemonState) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_state = appdaemon_state

    def create(self) -> HvacState | None:
        is_eco_mode = safe_bool(self.appdaemon_state.get_state(ECO_MODE_ENTITY))
        dhw_actual_temperature = safe_float(self.appdaemon_state.get_state(DHW_TEMPERATURE_ENTITY))
        dhw_target_temperature = safe_float(self.appdaemon_state.get_state(DHW_ENTITY, "temperature"))
        dhw_delta_temperature = safe_float(self.appdaemon_state.get_state(DHW_DELTA_TEMP_ENTITY))
        indoor_actual_temperature = safe_float(self.appdaemon_state.get_state(INDOOR_TEMPERATURE_ENTITY))
        heating_target_temperature = safe_float(self.appdaemon_state.get_state(HEATING_ENTITY, "temperature"))
        heating_mode = safe_str(self.appdaemon_state.get_state(HEATING_ENTITY))
        cooling_target_temperature = safe_float(self.appdaemon_state.get_state(COOLING_ENTITY, "temperature"))
        cooling_mode = safe_str(self.appdaemon_state.get_state(COOLING_ENTITY))
        heating_curve_target_high_temp = safe_float(
            self.appdaemon_state.get_state(HEATING_CURVE_TARGET_HIGH_TEMP_ENTITY)
        )
        heating_curve_target_low_temp = safe_float(self.appdaemon_state.get_state(HEATING_CURVE_TARGET_LOW_TEMP_ENTITY))
        temperature_adjustment = safe_float(self.appdaemon_state.get_state(TEMPERATURE_ADJUSTMENT_ENTITY))

        missing_mandatory = [
            name
            for name, value in [
                ("is_eco_mode", is_eco_mode),
                ("dhw_actual_temperature", dhw_actual_temperature),
                ("dhw_target_temperature", dhw_target_temperature),
                ("dhw_delta_temperature", dhw_delta_temperature),
                ("indoor_actual_temperature", indoor_actual_temperature),
                ("heating_target_temperature", heating_target_temperature),
                ("heating_mode", heating_mode),
                ("cooling_target_temperature", cooling_target_temperature),
                ("cooling_mode", cooling_mode),
                ("heating_curve_target_high_temp", heating_curve_target_high_temp),
                ("heating_curve_target_low_temp", heating_curve_target_low_temp),
                ("temperature_adjustment", temperature_adjustment),
            ]
            if value is None
        ]

        if missing_mandatory:
            self.appdaemon_logger.log(
                f"Can't create state, missing: {', '.join(missing_mandatory)}", level=logging.WARNING
            )
            return None

        assert is_eco_mode is not None
        assert dhw_actual_temperature is not None
        assert dhw_target_temperature is not None
        assert dhw_delta_temperature is not None
        assert indoor_actual_temperature is not None
        assert heating_target_temperature is not None
        assert heating_mode is not None
        assert cooling_target_temperature is not None
        assert cooling_mode is not None
        assert heating_curve_target_high_temp is not None
        assert heating_curve_target_low_temp is not None
        assert temperature_adjustment is not None

        return HvacState(
            is_eco_mode=is_eco_mode,
            dhw_actual_temperature=Celsius(dhw_actual_temperature),
            dhw_target_temperature=Celsius(dhw_target_temperature),
            dhw_delta_temperature=Celsius(dhw_delta_temperature),
            indoor_actual_temperature=Celsius(indoor_actual_temperature),
            heating_target_temperature=Celsius(heating_target_temperature),
            heating_mode=heating_mode,
            cooling_target_temperature=Celsius(cooling_target_temperature),
            cooling_mode=cooling_mode,
            heating_curve_target_high_temp=Celsius(heating_curve_target_high_temp),
            heating_curve_target_low_temp=Celsius(heating_curve_target_low_temp),
            temperature_adjustment=Celsius(temperature_adjustment),
        )
