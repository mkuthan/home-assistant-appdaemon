from decimal import Decimal
from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from appdaemon_protocols.appdaemon_state import AppdaemonState
from entities.entities import (
    AWAY_MODE_ENTITY,
    BATTERY_RESERVE_SOC_ENTITY,
    BATTERY_SOC_ENTITY,
    ECO_MODE_ENTITY,
    HEATING_ENTITY,
    HOURLY_PRICE_ENTITY,
    INVERTER_STORAGE_MODE_ENTITY,
    OUTDOOR_TEMPERATURE_ENTITY,
    PV_FORECAST_TODAY_ENTITY,
    PV_FORECAST_TOMORROW_ENTITY,
    SLOT1_DISCHARGE_CURRENT_ENTITY,
    SLOT1_DISCHARGE_ENABLED_ENTITY,
    SLOT1_DISCHARGE_TIME_ENTITY,
    SLOT2_DISCHARGE_CURRENT_ENTITY,
    SLOT2_DISCHARGE_ENABLED_ENTITY,
    SLOT2_DISCHARGE_TIME_ENTITY,
    WEATHER_FORECAST_ENTITY,
)
from solar.solar_state import SolarState
from solar.storage_mode import StorageMode
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.energy_price import EnergyPrice
from utils.safe_converters import safe_bool, safe_dict, safe_float, safe_list, safe_str


class SolarStateFactory(Protocol):
    def create(self) -> SolarState | None: ...


class DefaultSolarStateFactory:
    def __init__(
        self, appdaemon_logger: AppdaemonLogger, appdaemon_state: AppdaemonState, appdaemon_service: AppdaemonService
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_state = appdaemon_state
        self.appdaemon_service = appdaemon_service

    def create(self) -> SolarState | None:
        battery_soc = safe_float(self.appdaemon_state.get_state(BATTERY_SOC_ENTITY))
        battery_reserve_soc = safe_float(self.appdaemon_state.get_state(BATTERY_RESERVE_SOC_ENTITY))
        outdoor_temperature = safe_float(self.appdaemon_state.get_state(OUTDOOR_TEMPERATURE_ENTITY))
        is_away_mode = safe_bool(self.appdaemon_state.get_state(AWAY_MODE_ENTITY))
        is_eco_mode = safe_bool(self.appdaemon_state.get_state(ECO_MODE_ENTITY))
        inverter_storage_mode = safe_str(self.appdaemon_state.get_state(INVERTER_STORAGE_MODE_ENTITY))
        is_slot1_discharge_enabled = safe_bool(self.appdaemon_state.get_state(SLOT1_DISCHARGE_ENABLED_ENTITY))
        slot1_discharge_time = safe_str(self.appdaemon_state.get_state(SLOT1_DISCHARGE_TIME_ENTITY))
        slot1_discharge_current = safe_float(self.appdaemon_state.get_state(SLOT1_DISCHARGE_CURRENT_ENTITY))
        is_slot2_discharge_enabled = safe_bool(self.appdaemon_state.get_state(SLOT2_DISCHARGE_ENABLED_ENTITY))
        slot2_discharge_time = safe_str(self.appdaemon_state.get_state(SLOT2_DISCHARGE_TIME_ENTITY))
        slot2_discharge_current = safe_float(self.appdaemon_state.get_state(SLOT2_DISCHARGE_CURRENT_ENTITY))
        hvac_heating_mode = safe_str(self.appdaemon_state.get_state(HEATING_ENTITY))
        hourly_price = safe_float(self.appdaemon_state.get_state(HOURLY_PRICE_ENTITY))

        pv_forecast_today = safe_list(self.appdaemon_state.get_state(PV_FORECAST_TODAY_ENTITY, "detailedHourly"))
        pv_forecast_tomorrow = safe_list(self.appdaemon_state.get_state(PV_FORECAST_TOMORROW_ENTITY, "detailedHourly"))

        weather_forecast = safe_dict(
            self.appdaemon_service.call_service(
                "weather/get_forecasts", entity_id=WEATHER_FORECAST_ENTITY, type="hourly"
            )
        )

        price_forecast_today = safe_list(self.appdaemon_state.get_state(HOURLY_PRICE_ENTITY, "raw_today"))

        missing = []
        if battery_soc is None:
            missing.append("battery_soc")
        if battery_reserve_soc is None:
            missing.append("battery_reserve_soc")
        if outdoor_temperature is None:
            missing.append("outdoor_temperature")
        if is_away_mode is None:
            missing.append("is_away_mode")
        if is_eco_mode is None:
            missing.append("is_eco_mode")
        if inverter_storage_mode is None:
            missing.append("inverter_storage_mode")
        if is_slot1_discharge_enabled is None:
            missing.append("is_slot1_discharge_enabled")
        if slot1_discharge_time is None:
            missing.append("slot1_discharge_time")
        if slot1_discharge_current is None:
            missing.append("slot1_discharge_current")
        if is_slot2_discharge_enabled is None:
            missing.append("is_slot2_discharge_enabled")
        if slot2_discharge_time is None:
            missing.append("slot2_discharge_time")
        if slot2_discharge_current is None:
            missing.append("slot2_discharge_current")
        if hvac_heating_mode is None:
            missing.append("hvac_heating_mode")
        if hourly_price is None:
            missing.append("hourly_price")
        if pv_forecast_today is None:
            missing.append("pv_forecast_today")
        if pv_forecast_tomorrow is None:
            missing.append("pv_forecast_tomorrow")
        if weather_forecast is None:
            missing.append("weather_forecast")
        if price_forecast_today is None:
            missing.append("price_forecast_today")

        if missing:
            self.appdaemon_logger.warn(f"Missing: {', '.join(missing)}")
            return None

        assert battery_soc is not None
        assert battery_reserve_soc is not None
        assert outdoor_temperature is not None
        assert is_away_mode is not None
        assert is_eco_mode is not None
        assert inverter_storage_mode is not None
        assert is_slot1_discharge_enabled is not None
        assert slot1_discharge_time is not None
        assert slot1_discharge_current is not None
        assert is_slot2_discharge_enabled is not None
        assert slot2_discharge_time is not None
        assert slot2_discharge_current is not None
        assert hvac_heating_mode is not None
        assert hourly_price is not None
        assert pv_forecast_today is not None
        assert pv_forecast_tomorrow is not None
        assert weather_forecast is not None
        assert price_forecast_today is not None

        solar_state = SolarState(
            battery_soc=BatterySoc(battery_soc),
            battery_reserve_soc=BatterySoc(battery_reserve_soc),
            outdoor_temperature=outdoor_temperature,
            is_away_mode=is_away_mode,
            is_eco_mode=is_eco_mode,
            inverter_storage_mode=StorageMode(inverter_storage_mode),
            is_slot1_discharge_enabled=is_slot1_discharge_enabled,
            slot1_discharge_time=slot1_discharge_time,
            slot1_discharge_current=BatteryCurrent(slot1_discharge_current),
            is_slot2_discharge_enabled=is_slot2_discharge_enabled,
            slot2_discharge_time=slot2_discharge_time,
            slot2_discharge_current=BatteryCurrent(slot2_discharge_current),
            hvac_heating_mode=hvac_heating_mode,
            hourly_price=EnergyPrice.pln_per_mwh(Decimal.from_float(hourly_price)),
            pv_forecast_today=pv_forecast_today,
            pv_forecast_tomorrow=pv_forecast_tomorrow,
            weather_forecast=weather_forecast,
            price_forecast_today=price_forecast_today,
        )

        return solar_state
