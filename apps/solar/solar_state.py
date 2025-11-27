from dataclasses import dataclass

from solar.storage_mode import StorageMode
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.celsius import Celsius
from units.energy_price import EnergyPrice


@dataclass(frozen=True)
class SolarState:
    battery_soc: BatterySoc # current battery state of charge
    battery_reserve_soc: BatterySoc # configured battery reserve state of charge
    indoor_temperature: Celsius  # unused
    outdoor_temperature: Celsius  # unused
    is_away_mode: bool # away mode status
    is_eco_mode: bool # eco mode status
    inverter_storage_mode: StorageMode # current inverter storage mode
    is_slot1_discharge_enabled: bool # whether slot 1 discharge is enabled
    slot1_discharge_time: str # discharge time for slot 1
    slot1_discharge_current: BatteryCurrent # discharge current for slot 1
    hvac_heating_mode: str # heating mode
    hvac_heating_temperature: Celsius  # unused
    hourly_price: EnergyPrice # current hourly energy price
    pv_forecast_today: list # today's PV forecast
    pv_forecast_tomorrow: list # tomorrow's PV forecast
    weather_forecast: dict | None # weather forecast data
    price_forecast: list | None # energy price forecast