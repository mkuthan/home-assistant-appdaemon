from units.battery_current import BatteryCurrent
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh


def current_to_energy_kwh(current: BatteryCurrent, voltage: BatteryVoltage, duration_hours: int = 1) -> EnergyKwh:
    if duration_hours <= 0:
        raise ValueError(f"Duration must be positive, got {duration_hours}")
    energy_value = (current.value * voltage.value * duration_hours) / 1000
    return EnergyKwh(value=energy_value)


def energy_kwh_to_current(energy: EnergyKwh, voltage: BatteryVoltage, duration_hours: int = 1) -> BatteryCurrent:
    if duration_hours <= 0:
        raise ValueError(f"Duration must be positive, got {duration_hours}")
    current_value = (energy.value * 1000) / (voltage.value * duration_hours)
    return BatteryCurrent(value=current_value)
