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

    battery_capacity: EnergyKwh  # nominal battery capacity
    battery_voltage: BatteryVoltage  # nominal battery voltage
    battery_maximum_current: BatteryCurrent  # maximum battery discharge/charge current
    battery_reserve_soc_min: BatterySoc  # minimum reserve SOC
    battery_reserve_soc_margin: BatterySoc  # margin above minimum reserve SOC
    battery_reserve_soc_max: BatterySoc  # maximum reserve SOC

    temp_in: Celsius  # indoor temperature setpoint
    temp_out_threshold: Celsius  # outdoor temperature threshold for heating energy consumption in eco mode

    heating_cop_at_7c: float  # coefficient of heat-pump performance at 7 degrees Celsius
    heating_h: float  # coefficient representing building heat loss rate in kW/°C

    temp_out_fallback: Celsius  # outdoor temperature if no forecast available
    humidity_out_fallback: float  # outdoor humidity if no forecast available

    regular_consumption_away: EnergyKwh  # consumption when in away mode
    regular_consumption_day: EnergyKwh  # consumption during daytime
    regular_consumption_evening: EnergyKwh  # consumption during evening

    pv_export_min_price_margin: EnergyPrice  # margin above minimum price to export PV energy to grid

    battery_export_threshold_price: EnergyPrice  # minimum price threshold for selling battery energy to grid
    battery_export_threshold_energy: EnergyKwh  # minimum energy threshold for selling battery energy to grid

    night_low_tariff_time_start: time  # start time of night low tariff period (with margin)
    night_low_tariff_time_end: time  # end time of night low tariff period (with margin)

    day_low_tariff_time_start: time  # start time of day low tariff period (with margin)
    day_low_tariff_time_end: time  # end time of day low tariff period (with margin)
