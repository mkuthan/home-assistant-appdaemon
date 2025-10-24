from datetime import timedelta

from units.battery_current import BATTERY_CURRENT_ZERO, BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh
from utils.battery_converters import current_to_energy, energy_to_soc, soc_to_energy


def estimate_battery_reserve_soc(
    energy_reserve: EnergyKwh,
    battery_capacity: EnergyKwh,
    battery_reserve_soc_default: BatterySoc,
    battery_reserve_soc_margin: BatterySoc,
    battery_reserve_soc_max: BatterySoc,
) -> BatterySoc:
    reserve_ratio = (energy_reserve / battery_capacity) * 100.0
    reserve_soc = BatterySoc(min(reserve_ratio, 100.0))
    reserve_soc_plus_margin = battery_reserve_soc_default + battery_reserve_soc_margin + reserve_soc

    return min(reserve_soc_plus_margin, battery_reserve_soc_max)


def estimate_battery_surplus_energy(
    energy_reserve: EnergyKwh,
    battery_soc: BatterySoc,
    battery_capacity: EnergyKwh,
    battery_reserve_soc_default: BatterySoc,
    battery_reserve_soc_margin: BatterySoc,
) -> EnergyKwh:
    reserve_soc = energy_to_soc(energy_reserve, battery_capacity)
    surplus_soc = battery_soc - reserve_soc - battery_reserve_soc_default - battery_reserve_soc_margin

    return soc_to_energy(surplus_soc, battery_capacity)


def estimate_battery_max_soc(
    energy_surplus: EnergyKwh,
    battery_soc: BatterySoc,
    battery_capacity: EnergyKwh,
) -> BatterySoc:
    surplus_ratio = (energy_surplus / battery_capacity) * 100.0
    surplus_soc = BatterySoc(min(surplus_ratio, 100.0))
    return battery_soc + surplus_soc


def estimate_time_to_charge(
    soc_deficit: BatterySoc,
    battery_capacity: EnergyKwh,
    battery_current: BatteryCurrent,
    battery_voltage: BatteryVoltage,
) -> timedelta:
    if battery_current == BATTERY_CURRENT_ZERO:
        raise ValueError("Battery current must be greater than zero to estimate charging time.")

    energy_needed = soc_to_energy(soc_deficit, battery_capacity)
    power_kw = current_to_energy(battery_current, battery_voltage)
    hours_needed = energy_needed / power_kw

    return timedelta(hours=hours_needed)
