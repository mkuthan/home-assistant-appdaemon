import pytest
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from utils.battery_estimators import (
    estimate_battery_max_soc,
    estimate_battery_reserve_soc,
    estimate_battery_surplus_energy,
)


@pytest.mark.parametrize(
    (
        "energy_reserve",
        "battery_capacity",
        "battery_reserve_soc_default",
        "battery_reserve_soc_margin",
        "battery_reserve_soc_max",
        "expected",
    ),
    [
        # Energy reserve is half of capacity, no default or margin
        (EnergyKwh(5.0), EnergyKwh(10.0), BatterySoc(20.0), BatterySoc(15.0), BatterySoc(100.0), BatterySoc(85.0)),
        # Energy reserve exceeds capacity (should be clamped to 100%)
        (EnergyKwh(10.0), EnergyKwh(10.0), BatterySoc(20.0), BatterySoc(15.0), BatterySoc(100.0), BatterySoc(100.0)),
        # No energy reserve, only default and margin
        (EnergyKwh(0.0), EnergyKwh(10.0), BatterySoc(20.0), BatterySoc(15.0), BatterySoc(100.0), BatterySoc(35.0)),
        # Energy reserve + default + margin exceeds max (should be clamped to max)
        (EnergyKwh(8.0), EnergyKwh(10.0), BatterySoc(20.0), BatterySoc(15.0), BatterySoc(80.0), BatterySoc(80.0)),
    ],
)
def test_estimate_battery_reserve_soc(
    energy_reserve: EnergyKwh,
    battery_capacity: EnergyKwh,
    battery_reserve_soc_default: BatterySoc,
    battery_reserve_soc_margin: BatterySoc,
    battery_reserve_soc_max: BatterySoc,
    expected: BatterySoc,
) -> None:
    result = estimate_battery_reserve_soc(
        energy_reserve,
        battery_capacity,
        battery_reserve_soc_default,
        battery_reserve_soc_margin,
        battery_reserve_soc_max,
    )
    assert result.value == pytest.approx(expected.value)


@pytest.mark.parametrize(
    (
        "energy_reserve",
        "battery_soc",
        "battery_capacity",
        "battery_reserve_soc_default",
        "battery_reserve_soc_margin",
        "expected",
    ),
    [
        # 2.5 kWh → 25%, surplus 80% - (25% + 20% + 15%) → 2.0 kWh
        (EnergyKwh(2.5), BatterySoc(80.0), EnergyKwh(10.0), BatterySoc(20.0), BatterySoc(15.0), EnergyKwh(2.0)),
        # No surplus, exactly at reserve + default + margin
        (EnergyKwh(2.5), BatterySoc(60.0), EnergyKwh(10.0), BatterySoc(20.0), BatterySoc(15.0), EnergyKwh(0.0)),
        # No surplus, below reserve + default + margin
        (EnergyKwh(2.5), BatterySoc(50.0), EnergyKwh(10.0), BatterySoc(20.0), BatterySoc(15.0), EnergyKwh(0.0)),
        # 5.0 kWh → 25%, surplus 80% - (25% + 20% + 15%) → 4.0 kWh
        (EnergyKwh(5.0), BatterySoc(80.0), EnergyKwh(20.0), BatterySoc(20.0), BatterySoc(15.0), EnergyKwh(4.0)),
    ],
)
def test_estimate_battery_surplus_energy(
    energy_reserve: EnergyKwh,
    battery_soc: BatterySoc,
    battery_capacity: EnergyKwh,
    battery_reserve_soc_default: BatterySoc,
    battery_reserve_soc_margin: BatterySoc,
    expected: float,
) -> None:
    result = estimate_battery_surplus_energy(
        energy_reserve,
        battery_soc,
        battery_capacity,
        battery_reserve_soc_default,
        battery_reserve_soc_margin,
    )
    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("energy_surplus", "battery_soc", "battery_capacity", "expected"),
    [
        # 5.0 kWh surplus + 30% battery (10kWh) → 80%
        (EnergyKwh(5.0), BatterySoc(30.0), EnergyKwh(10.0), BatterySoc(80.0)),
        # 10.0 kWh surplus + 30% battery (10kWh) → clamped to 100%
        (EnergyKwh(10.0), BatterySoc(30.0), EnergyKwh(10.0), BatterySoc(100.0)),
        # No surplus, battery stays the same
        (EnergyKwh(0.0), BatterySoc(50.0), EnergyKwh(10.0), BatterySoc(50.0)),
        # 5.0 kWh surplus + 20% battery (20kWh) → 45%
        (EnergyKwh(5.0), BatterySoc(20.0), EnergyKwh(20.0), BatterySoc(45.0)),
    ],
)
def test_estimate_battery_max_soc(
    energy_surplus: EnergyKwh,
    battery_soc: BatterySoc,
    battery_capacity: EnergyKwh,
    expected: BatterySoc,
) -> None:
    result = estimate_battery_max_soc(energy_surplus, battery_soc, battery_capacity)
    assert result.value == pytest.approx(expected.value)
