from decimal import Decimal

from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from utils.battery_converters import energy_to_soc, soc_to_energy


def estimate_battery_reserve_soc(
    energy_reserve: EnergyKwh,
    battery_capacity: EnergyKwh,
    battery_reserve_soc_default: BatterySoc,
    battery_reserve_soc_margin: BatterySoc,
    battery_reserve_soc_max: BatterySoc,
) -> BatterySoc:
    reserve_ratio = Decimal(str(energy_reserve.ratio(battery_capacity))) * Decimal("100")
    reserve_soc = BatterySoc(value=min(reserve_ratio, Decimal("100")))
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
    surplus_ratio = Decimal(str(energy_surplus.ratio(battery_capacity))) * Decimal("100")
    surplus_soc = BatterySoc(value=min(surplus_ratio, Decimal("100")))
    return battery_soc + surplus_soc
