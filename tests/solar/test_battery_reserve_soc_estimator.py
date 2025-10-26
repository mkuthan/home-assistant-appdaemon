from dataclasses import replace
from datetime import datetime
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
        battery_reserve_soc_min=BatterySoc(20.0),
        battery_reserve_soc_margin=BatterySoc(5.0),
        battery_reserve_soc_max=BatterySoc(100.0),
    )

    return BatteryReserveSocEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        config=config,
        forecast_factory=mock_forecast_factory,
    )


def test_estimate_soc_tomorrow_at_7_am_when_higher_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_reserve_soc=BatterySoc(30.0))

    now = datetime.fromisoformat("2025-10-10T22:00:00+00:00")
    period_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    hourly_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(2.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_soc_tomorrow_at_7_am(state, now, period_hours)

    mock_production_forecast.hourly.assert_called_once_with(tomorrow_7_am, period_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(tomorrow_7_am, period_hours)

    assert battery_reserve_soc == BatterySoc(65.0)


def test_estimate_soc_tomorrow_at_7_am_when_lower_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_reserve_soc=BatterySoc(50.0))

    now = datetime.fromisoformat("2025-10-10T22:00:00+00:00")
    period_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    hourly_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(5.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_soc_tomorrow_at_7_am(state, now, period_hours)

    mock_production_forecast.hourly.assert_called_once_with(tomorrow_7_am, period_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(tomorrow_7_am, period_hours)

    assert battery_reserve_soc is None
