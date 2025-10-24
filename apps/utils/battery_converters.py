from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh


def energy_to_soc(energy_kwh: EnergyKwh, battery_capacity_kwh: EnergyKwh) -> BatterySoc:
    soc_value = (energy_kwh / battery_capacity_kwh) * 100.0
    return BatterySoc(value=min(soc_value, BatterySoc._MAX_VALUE))


def soc_to_energy(battery_soc: BatterySoc, battery_capacity_kwh: EnergyKwh) -> EnergyKwh:
    energy_value = (battery_soc.value / 100.0) * battery_capacity_kwh.value
    return EnergyKwh(value=energy_value)


def current_to_energy(current: BatteryCurrent, voltage: BatteryVoltage, duration_hours: int = 1) -> EnergyKwh:
    if duration_hours <= 0:
        raise ValueError(f"Duration must be positive, got {duration_hours}")
    energy_value = (current.value * voltage.value * duration_hours) / 1000
    return EnergyKwh(value=energy_value)


def energy_to_current(energy: EnergyKwh, voltage: BatteryVoltage, duration_hours: int = 1) -> BatteryCurrent:
    if duration_hours <= 0:
        raise ValueError(f"Duration must be positive, got {duration_hours}")
    current_value = (energy.value * 1000) / (voltage.value * duration_hours)
    return BatteryCurrent(value=current_value)
