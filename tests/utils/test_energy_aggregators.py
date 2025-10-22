import pytest
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod
from utils.energy_aggregators import EnergyAggregators


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

    total_surplus = EnergyAggregators.total_surplus(hourly_consumptions, hourly_productions)

    assert total_surplus == EnergyKwh(0.5)


def test_total_surplus_capped(any_hourly_period: HourlyPeriod) -> None:
    hourly_productions = [
        HourlyProductionEnergy(any_hourly_period, EnergyKwh(0.5)),
    ]

    hourly_consumptions = [
        HourlyConsumptionEnergy(any_hourly_period, EnergyKwh(2.0)),
    ]

    total_surplus = EnergyAggregators.total_surplus(hourly_consumptions, hourly_productions)

    assert total_surplus == EnergyKwh(0.0)


def test_cumulative_deficit() -> None:
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
        HourlyConsumptionEnergy(period_2, EnergyKwh(2.0)),
        HourlyConsumptionEnergy(period_3, EnergyKwh(1.0)),
    ]

    max_deficit = EnergyAggregators.maximum_cumulative_deficit(hourly_consumptions, hourly_productions)

    assert max_deficit == EnergyKwh(1.5)


def test_cumulative_deficit_capped(any_hourly_period: HourlyPeriod) -> None:
    hourly_productions = [
        HourlyProductionEnergy(any_hourly_period, EnergyKwh(2.0)),
    ]

    hourly_consumptions = [
        HourlyConsumptionEnergy(any_hourly_period, EnergyKwh(1.0)),
    ]

    max_deficit = EnergyAggregators.maximum_cumulative_deficit(hourly_consumptions, hourly_productions)

    assert max_deficit == EnergyKwh(0.0)
