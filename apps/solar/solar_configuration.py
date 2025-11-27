from dataclasses import dataclass
from datetime import time

from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.celsius import Celsius
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice


@dataclass(frozen=True)
class SolarConfiguration:
    time_zone: str

    battery_capacity: EnergyKwh
    battery_voltage: BatteryVoltage
    battery_maximum_current: BatteryCurrent
    battery_reserve_soc_min: BatterySoc
    battery_reserve_soc_margin: BatterySoc
    battery_reserve_soc_max: BatterySoc

    temp_in: Celsius
    temp_out_threshold: Celsius

    heating_cop_at_7c: float
    heating_h: float

    temp_out_fallback: Celsius
    humidity_out_fallback: float

    regular_consumption_away: EnergyKwh
    regular_consumption_day: EnergyKwh
    regular_consumption_evening: EnergyKwh

    pv_export_min_price_margin: EnergyPrice

    battery_export_threshold_price: EnergyPrice
    battery_export_threshold_energy: EnergyKwh

    night_low_tariff_time_start: time
    night_low_tariff_time_end: time

    day_low_tariff_time_start: time
    day_low_tariff_time_end: time
