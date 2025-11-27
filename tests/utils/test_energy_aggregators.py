import pytest
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod
from utils.energy_aggregators import maximum_cumulative_deficit, total_surplus


@pytest.fixture
def any_hourly_period() -> HourlyPeriod:
    return HourlyPeriod.parse("2025-10-21T10:00:00+00:00")


def test_total_surplus() -> None:
    period_1 = HourlyPeriod.parse("2025-10-21T07:00:00+00:00")
    period_2 = HourlyPeriod.parse("2025-10-21T08:00:00+00:00")
    period_3 = HourlyPeriod.parse("2025-10-21T09:00:00+00:00")

    hourly_productions = [
        HourlyProductionEnergy(period_1, EnergyKwh(0.5)),
        HourlyProductionEnergy(period_2, EnergyKwh(1.0)),
        HourlyProductionEnergy(period_3, EnergyKwh(2.0)),
    ]

    hourly_consumptions = [
        HourlyConsumptionEnergy(period_1, EnergyKwh(1.0)),
        HourlyConsumptionEnergy(period_2, EnergyKwh(1.0)),
        HourlyConsumptionEnergy(period_3, EnergyKwh(1.0)),
    ]

    result = total_surplus(hourly_consumptions, hourly_productions)

    assert result == EnergyKwh(0.5)


def test_total_surplus_capped(any_hourly_period: HourlyPeriod) -> None:
    hourly_productions = [
        HourlyProductionEnergy(any_hourly_period, EnergyKwh(0.5)),
    ]

    hourly_consumptions = [
        HourlyConsumptionEnergy(any_hourly_period, EnergyKwh(2.0)),
    ]

    result = total_surplus(hourly_consumptions, hourly_productions)

    assert result == EnergyKwh(0.0)


def test_cumulative_deficit() -> None:
    period_1 = HourlyPeriod.parse("2025-10-21T07:00:00+00:00")
    period_2 = HourlyPeriod.parse("2025-10-21T08:00:00+00:00")
    period_3 = HourlyPeriod.parse("2025-10-21T09:00:00+00:00")
    period_4 = HourlyPeriod.parse("2025-10-21T10:00:00+00:00")

    hourly_productions = [
        HourlyProductionEnergy(period_1, EnergyKwh(0.25)),
        HourlyProductionEnergy(period_2, EnergyKwh(1.0)),
        HourlyProductionEnergy(period_3, EnergyKwh(2.0)),
        HourlyProductionEnergy(period_4, EnergyKwh(0.25)),
    ]

    hourly_consumptions = [
        HourlyConsumptionEnergy(period_1, EnergyKwh(0.5)),
        HourlyConsumptionEnergy(period_2, EnergyKwh(2.0)),
        HourlyConsumptionEnergy(period_3, EnergyKwh(1.0)),
        HourlyConsumptionEnergy(period_4, EnergyKwh(0.5)),
    ]

    result = maximum_cumulative_deficit(hourly_consumptions, hourly_productions)

    assert result == EnergyKwh(1.25)


def test_cumulative_deficit_capped(any_hourly_period: HourlyPeriod) -> None:
    hourly_productions = [
        HourlyProductionEnergy(any_hourly_period, EnergyKwh(2.0)),
    ]

    hourly_consumptions = [
        HourlyConsumptionEnergy(any_hourly_period, EnergyKwh(1.0)),
    ]

    result = maximum_cumulative_deficit(hourly_consumptions, hourly_productions)

    assert result == EnergyKwh(0.0)
