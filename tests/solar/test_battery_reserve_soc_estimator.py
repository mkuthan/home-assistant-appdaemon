from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


@pytest.fixture
def battery_reserve_soc_estimator(
    config: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_forecast_factory: Mock,
) -> BatteryReserveSocEstimator:
    config = replace(
        config,
        battery_capacity=EnergyKwh(10.0),
        battery_reserve_soc_min=BatterySoc(value=Decimal("20.0")),
        battery_reserve_soc_margin=BatterySoc(value=Decimal("5.0")),
        battery_reserve_soc_max=BatterySoc(value=Decimal("100.0")),
    )

    return BatteryReserveSocEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        config=config,
        forecast_factory=mock_forecast_factory,
    )


def test_estimator_when_higher_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_reserve_soc=BatterySoc(value=Decimal("30.0")))

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    period_hours = 6

    hourly_period = HourlyPeriod.parse("2025-10-10T16:00:00+00:00")

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(2.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator(state, period_start, period_hours)

    mock_production_forecast.hourly.assert_called_once_with(period_start, period_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(period_start, period_hours)

    assert battery_reserve_soc == BatterySoc(value=Decimal("65.0"))


def test_estimator_when_lower_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_reserve_soc=BatterySoc(value=Decimal("50.0")))

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    period_hours = 6

    hourly_period = HourlyPeriod.parse("2025-10-10T16:00:00+00:00")

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(5.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator(state, period_start, period_hours)

    mock_production_forecast.hourly.assert_called_once_with(period_start, period_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(period_start, period_hours)

    assert battery_reserve_soc is None
