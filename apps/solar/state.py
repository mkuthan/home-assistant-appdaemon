from dataclasses import dataclass

from solar.storage_mode import StorageMode
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.energy_price import EnergyPrice


@dataclass(frozen=True)
class State:
    battery_soc: BatterySoc
    battery_reserve_soc: BatterySoc
    indoor_temperature: float
    outdoor_temperature: float
    is_away_mode: bool
    is_eco_mode: bool
    inverter_storage_mode: StorageMode
    is_slot1_discharge_enabled: bool
    slot1_discharge_time: str
    slot1_discharge_current: BatteryCurrent
    is_slot2_discharge_enabled: bool
    slot2_discharge_time: str
    slot2_discharge_current: BatteryCurrent
    hvac_heating_mode: str
    hourly_price: EnergyPrice
    pv_forecast_today: list
    pv_forecast_tomorrow: list
    weather_forecast: dict
    price_forecast_today: list
