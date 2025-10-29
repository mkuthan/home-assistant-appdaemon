from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from appdaemon_protocols.appdaemon_state import AppdaemonState
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
        is_eco_mode = safe_bool(self.appdaemon_state.get_state("input_boolean.eco_mode"))

        dhw_temperature = safe_float(
            self.appdaemon_state.get_state("water_heater.panasonic_heat_pump_main_dhw_target_temp", "temperature")
        )

        heating_temperature = safe_float(
            self.appdaemon_state.get_state("climate.panasonic_heat_pump_main_z1_temp", "temperature")
        )

        heating_mode = safe_str(self.appdaemon_state.get_state("climate.panasonic_heat_pump_main_z1_temp"))

        cooling_temperature = safe_float(
            self.appdaemon_state.get_state("climate.panasonic_heat_pump_main_z1_temp_cooling", "temperature")
        )

        cooling_mode = safe_str(self.appdaemon_state.get_state("climate.panasonic_heat_pump_main_z1_temp_cooling"))

        missing = []
        if is_eco_mode is None:
            missing.append("is_eco_mode")
        if dhw_temperature is None:
            missing.append("dhw_temperature")
        if heating_temperature is None:
            missing.append("heating_temperature")
        if heating_mode is None:
            missing.append("heating_mode")
        if cooling_temperature is None:
            missing.append("cooling_temperature")
        if cooling_mode is None:
            missing.append("cooling_mode")

        if missing:
            self.appdaemon_logger.warn(f"Missing: {', '.join(missing)}")
            return None

        assert is_eco_mode is not None
        assert dhw_temperature is not None
        assert heating_temperature is not None
        assert heating_mode is not None
        assert cooling_temperature is not None
        assert cooling_mode is not None

        return HvacState(
            is_eco_mode=is_eco_mode,
            dhw_temperature=Celsius(dhw_temperature),
            heating_temperature=Celsius(heating_temperature),
            heating_mode=heating_mode,
            cooling_temperature=Celsius(cooling_temperature),
            cooling_mode=cooling_mode,
        )
