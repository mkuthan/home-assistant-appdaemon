from dataclasses import dataclass

from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice


@dataclass(frozen=True)
class SolarConfiguration:
    battery_capacity: EnergyKwh  # nominal battery capacity
    battery_voltage: BatteryVoltage  # nominal battery voltage
    battery_maximum_current: BatteryCurrent  # maximum battery discharge/charge current
    battery_reserve_soc_min: BatterySoc  # minimum reserve SOC
    battery_reserve_soc_margin: BatterySoc  # margin above minimum reserve SOC

    heating_cop_at_7c: float  # coefficient of heat-pump performance at 7 degrees Celsius
    heating_h: float  # coefficient representing building heat loss rate in kW/°C

    temp_out_fallback: float  # outdoor temperature if no forecast available
    humidity_out_fallback: float  # outdoor humidity if no forecast available

    evening_start_hour: int  # hour when evening consumption rate begins
    regular_consumption_away: EnergyKwh  # consumption when in away mode
    regular_consumption_day: EnergyKwh  # consumption during daytime (before evening_start_hour)
    regular_consumption_evening: EnergyKwh  # consumption during evening (evening_start_hour onwards)

    pv_export_threshold_price: EnergyPrice  # minimum price threshold for selling PV energy to grid

    battery_export_threshold_price: EnergyPrice  # minimum price threshold for selling battery energy to grid
    battery_export_threshold_energy: EnergyKwh  # minimum energy threshold for selling battery energy to grid
