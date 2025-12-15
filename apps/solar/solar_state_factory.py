import logging
from decimal import Decimal
from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_state import AppdaemonState
from entities.entities import (
    AWAY_MODE_ENTITY,
    BATTERY_RESERVE_SOC_ENTITY,
    BATTERY_SOC_ENTITY,
    ECO_MODE_ENTITY,
    HEATING_ENTITY,
    INDOOR_TEMPERATURE_ENTITY,
    INVERTER_STORAGE_MODE_ENTITY,
    OUTDOOR_TEMPERATURE_ENTITY,
    PRICE_FORECAST_ENTITY,
    PV_FORECAST_TODAY_ENTITY,
    PV_FORECAST_TOMORROW_ENTITY,
    SLOT1_DISCHARGE_CURRENT_ENTITY,
    SLOT1_DISCHARGE_ENABLED_ENTITY,
    SLOT1_DISCHARGE_TIME_ENTITY,
    WEATHER_FORECAST_ENTITY,
)
from solar.solar_state import SolarState
from solar.storage_mode import StorageMode
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.celsius import Celsius
from units.energy_price import EnergyPrice
from utils.safe_converters import safe_bool, safe_float, safe_list, safe_str


class SolarStateFactory(Protocol):
    def create(self) -> SolarState | None: ...


class DefaultSolarStateFactory:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        appdaemon_state: AppdaemonState,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_state = appdaemon_state

    def create(self) -> SolarState | None:
        battery_soc = safe_float(self.appdaemon_state.get_state(BATTERY_SOC_ENTITY))
        battery_reserve_soc = safe_float(self.appdaemon_state.get_state(BATTERY_RESERVE_SOC_ENTITY))
        indoor_temperature = safe_float(self.appdaemon_state.get_state(INDOOR_TEMPERATURE_ENTITY))
        outdoor_temperature = safe_float(self.appdaemon_state.get_state(OUTDOOR_TEMPERATURE_ENTITY))
        is_away_mode = safe_bool(self.appdaemon_state.get_state(AWAY_MODE_ENTITY))
        is_eco_mode = safe_bool(self.appdaemon_state.get_state(ECO_MODE_ENTITY))
        inverter_storage_mode = safe_str(self.appdaemon_state.get_state(INVERTER_STORAGE_MODE_ENTITY))
        is_slot1_discharge_enabled = safe_bool(self.appdaemon_state.get_state(SLOT1_DISCHARGE_ENABLED_ENTITY))
        slot1_discharge_time = safe_str(self.appdaemon_state.get_state(SLOT1_DISCHARGE_TIME_ENTITY))
        slot1_discharge_current = safe_float(self.appdaemon_state.get_state(SLOT1_DISCHARGE_CURRENT_ENTITY))
        hvac_heating_mode = safe_str(self.appdaemon_state.get_state(HEATING_ENTITY))
        hvac_heating_temperature = safe_float(self.appdaemon_state.get_state(HEATING_ENTITY, "temperature"))
        hourly_price = safe_float(self.appdaemon_state.get_state(PRICE_FORECAST_ENTITY))

        pv_forecast_today = safe_list(self.appdaemon_state.get_state(PV_FORECAST_TODAY_ENTITY, "detailedHourly"))
        pv_forecast_tomorrow = safe_list(self.appdaemon_state.get_state(PV_FORECAST_TOMORROW_ENTITY, "detailedHourly"))

        weather_forecast = safe_list(self.appdaemon_state.get_state(WEATHER_FORECAST_ENTITY, "forecast"))

        price_forecast = safe_list(self.appdaemon_state.get_state(PRICE_FORECAST_ENTITY, "prices"))

        missing_mandatory = [
            name
            for name, value in [
                ("battery_soc", battery_soc),
                ("battery_reserve_soc", battery_reserve_soc),
                ("indoor_temperature", indoor_temperature),
                ("outdoor_temperature", outdoor_temperature),
                ("is_away_mode", is_away_mode),
                ("is_eco_mode", is_eco_mode),
                ("inverter_storage_mode", inverter_storage_mode),
                ("is_slot1_discharge_enabled", is_slot1_discharge_enabled),
                ("slot1_discharge_time", slot1_discharge_time),
                ("slot1_discharge_current", slot1_discharge_current),
                ("hvac_heating_mode", hvac_heating_mode),
                ("hvac_heating_temperature", hvac_heating_temperature),
                ("hourly_price", hourly_price),
                ("pv_forecast_today", pv_forecast_today),
                ("pv_forecast_tomorrow", pv_forecast_tomorrow),
            ]
            if value is None
        ]

        if missing_mandatory:
            self.appdaemon_logger.log(
                f"Can't create state, missing: {', '.join(missing_mandatory)}", level=logging.WARNING
            )
            return None

        assert battery_soc is not None
        assert battery_reserve_soc is not None
        assert indoor_temperature is not None
        assert outdoor_temperature is not None
        assert is_away_mode is not None
        assert is_eco_mode is not None
        assert inverter_storage_mode is not None
        assert is_slot1_discharge_enabled is not None
        assert slot1_discharge_time is not None
        assert slot1_discharge_current is not None
        assert hvac_heating_mode is not None
        assert hvac_heating_temperature is not None
        assert hourly_price is not None
        assert pv_forecast_today is not None
        assert pv_forecast_tomorrow is not None

        missing_optional = [
            name
            for name, value in [
                ("weather_forecast", weather_forecast),
                ("price_forecast", price_forecast),
            ]
            if value is None
        ]

        if missing_optional:
            self.appdaemon_logger.log(f"Fallback mode, missing: {', '.join(missing_optional)}", level=logging.WARNING)

        solar_state = SolarState(
            battery_soc=BatterySoc(battery_soc),
            battery_reserve_soc=BatterySoc(battery_reserve_soc),
            indoor_temperature=Celsius(indoor_temperature),
            outdoor_temperature=Celsius(outdoor_temperature),
            is_away_mode=is_away_mode,
            is_eco_mode=is_eco_mode,
            inverter_storage_mode=StorageMode(inverter_storage_mode),
            is_slot1_discharge_enabled=is_slot1_discharge_enabled,
            slot1_discharge_time=slot1_discharge_time,
            slot1_discharge_current=BatteryCurrent(slot1_discharge_current),
            hvac_heating_mode=hvac_heating_mode,
            hvac_heating_temperature=Celsius(hvac_heating_temperature),
            hourly_price=EnergyPrice.pln_per_mwh(Decimal.from_float(hourly_price)),
            pv_forecast_today=pv_forecast_today,
            pv_forecast_tomorrow=pv_forecast_tomorrow,
            weather_forecast=weather_forecast,
            price_forecast=price_forecast,
        )

        return solar_state
