from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh


def energy_to_soc(energy_kwh: EnergyKwh, battery_capacity_kwh: EnergyKwh) -> BatterySoc:
    soc_value = (energy_kwh / battery_capacity_kwh) * 100.0
    return BatterySoc(value=min(soc_value, BatterySoc._MAX_VALUE))


def soc_to_energy(battery_soc: BatterySoc, battery_capacity_kwh: EnergyKwh) -> EnergyKwh:
    energy_value = (battery_soc.value / 100.0) * battery_capacity_kwh.value
    return EnergyKwh(value=energy_value)
