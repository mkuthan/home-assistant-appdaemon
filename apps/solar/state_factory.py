from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from appdaemon_protocols.appdaemon_state import AppdaemonState
from solar.state import State
from solar.storage_mode import StorageMode
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.energy_price import EnergyPrice
from utils.safe_converters import safe_bool, safe_dict, safe_float, safe_list, safe_str


class StateFactory(Protocol):
    def create(self) -> State | None: ...


class DefaultStateFactory:
    BATTERY_SOC_ENTITY = "sensor.solis_remaining_battery_capacity"
    BATTERY_RESERVE_SOC_ENTITY = "number.solis_control_battery_reserve_soc"
    HOURLY_PRICE_ENTITY = "sensor.rce"

    def __init__(
        self, appdaemon_logger: AppdaemonLogger, appdaemon_state: AppdaemonState, appdaemon_service: AppdaemonService
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_state = appdaemon_state
        self.appdaemon_service = appdaemon_service

    def create(self) -> State | None:
        battery_soc = safe_float(self.appdaemon_state.get_state(self.BATTERY_SOC_ENTITY))
        battery_reserve_soc = safe_float(self.appdaemon_state.get_state(self.BATTERY_RESERVE_SOC_ENTITY))
        indoor_temperature = safe_float(self.appdaemon_state.get_state("sensor.heishamon_z1_actual_temperature"))
        outdoor_temperature = safe_float(self.appdaemon_state.get_state("sensor.heishamon_outside_ambient_temperature"))
        is_away_mode = safe_bool(self.appdaemon_state.get_state("input_boolean.away_mode"))
        is_eco_mode = safe_bool(self.appdaemon_state.get_state("input_boolean.eco_mode"))
        inverter_storage_mode = safe_str(self.appdaemon_state.get_state("select.solis_control_storage_mode"))
        is_slot1_discharge_enabled = safe_bool(self.appdaemon_state.get_state("switch.solis_control_slot1_discharge"))
        slot1_discharge_time = safe_str(self.appdaemon_state.get_state("text.solis_control_slot1_discharge_time"))
        slot1_discharge_current = safe_float(
            self.appdaemon_state.get_state("number.solis_control_slot1_discharge_current")
        )
        hvac_heating_mode = safe_str(self.appdaemon_state.get_state("climate.panasonic_heat_pump_main_z1_temp"))
        hourly_price = safe_float(self.appdaemon_state.get_state(self.HOURLY_PRICE_ENTITY))

        pv_forecast_today = safe_list(
            self.appdaemon_state.get_state("sensor.solcast_pv_forecast_forecast_today", "detailedHourly")
        )
        pv_forecast_tomorrow = safe_list(
            self.appdaemon_state.get_state("sensor.solcast_pv_forecast_forecast_tomorrow", "detailedHourly")
        )
        pv_forecast_day_3 = safe_list(
            self.appdaemon_state.get_state("sensor.solcast_pv_forecast_forecast_day_3", "detailedHourly")
        )

        weather_forecast = safe_dict(
            self.appdaemon_service.call_service(
                "weather/get_forecasts", entity_id="weather.forecast_wieprz", type="hourly"
            )
        )

        price_forecast_today = safe_list(self.appdaemon_state.get_state("sensor.rce", "raw_today"))

        missing = []
        if battery_soc is None:
            missing.append("battery_soc")
        if battery_reserve_soc is None:
            missing.append("battery_reserve_soc")
        if indoor_temperature is None:
            missing.append("indoor_temperature")
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
        if hvac_heating_mode is None:
            missing.append("hvac_heating_mode")
        if hourly_price is None:
            missing.append("hourly_price")
        if pv_forecast_today is None:
            missing.append("pv_forecast_today")
        if pv_forecast_tomorrow is None:
            missing.append("pv_forecast_tomorrow")
        if pv_forecast_day_3 is None:
            missing.append("pv_forecast_day_3")
        if weather_forecast is None:
            missing.append("weather_forecast")
        if price_forecast_today is None:
            missing.append("price_forecast_today")

        if missing:
            self.appdaemon_logger.warn(f"Missing: {', '.join(missing)}")
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
        assert hourly_price is not None
        assert pv_forecast_today is not None
        assert pv_forecast_tomorrow is not None
        assert pv_forecast_day_3 is not None
        assert weather_forecast is not None
        assert price_forecast_today is not None

        solar_state = State(
            battery_soc=BatterySoc(battery_soc),
            battery_reserve_soc=BatterySoc(battery_reserve_soc),
            indoor_temperature=indoor_temperature,
            outdoor_temperature=outdoor_temperature,
            is_away_mode=is_away_mode,
            is_eco_mode=is_eco_mode,
            inverter_storage_mode=StorageMode(inverter_storage_mode),
            is_slot1_discharge_enabled=is_slot1_discharge_enabled,
            slot1_discharge_time=slot1_discharge_time,
            slot1_discharge_current=BatteryCurrent(slot1_discharge_current),
            hvac_heating_mode=hvac_heating_mode,
            hourly_price=EnergyPrice.pln_per_mwh(hourly_price),
            pv_forecast_today=pv_forecast_today,
            pv_forecast_tomorrow=pv_forecast_tomorrow,
            pv_forecast_day_3=pv_forecast_day_3,
            weather_forecast=weather_forecast,
            price_forecast_today=price_forecast_today,
        )

        return solar_state
