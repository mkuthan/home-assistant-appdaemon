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
    low_tariff_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    hourly_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(2.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_soc_tomorrow_at_7_am(state, now)

    mock_production_forecast.hourly.assert_called_once_with(tomorrow_7_am, low_tariff_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(tomorrow_7_am, low_tariff_hours)

    assert battery_reserve_soc == BatterySoc(65.0)


def test_estimate_soc_tomorrow_at_7_am_when_lower_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_reserve_soc=BatterySoc(50.0))

    now = datetime.fromisoformat("2025-10-10T22:00:00+00:00")
    low_tariff_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    hourly_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(5.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_soc_tomorrow_at_7_am(state, now)

    mock_production_forecast.hourly.assert_called_once_with(tomorrow_7_am, low_tariff_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(tomorrow_7_am, low_tariff_hours)

    assert battery_reserve_soc is None


def test_estimate_soc_today_at_4_pm_when_grid_charging_needed(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(40.0), battery_reserve_soc=BatterySoc(20.0))

    now = datetime.fromisoformat("2025-10-10T15:00:00+00:00")

    today_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")

    afternoon_period = HourlyPeriod(now)
    evening_period = HourlyPeriod(today_4_pm)

    # Evening forecast: deficit requires 60% SoC target
    mock_consumption_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(6.0))],
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(1.0))],
    ]
    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(0.5))],
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(1.5))],
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_soc_today_at_4_pm(state, now)

    # Evening deficit: 6.0 kWh - 0.5 kWh = 5.5 kWh
    # Afternoon surplus: 1.5 kWh - 1.0 kWh = 0.5 kWh
    # Net deficit: 5.5 kWh - 0.5 kWh = 5.0 kWh
    # Required SoC from battery: 5.0 kWh / 10.0 kWh = 50% + 20% min + 5% margin = 75%
    # TODO: improve the implementation to account for solar surplus energy
    assert battery_reserve_soc == BatterySoc(80.0)
