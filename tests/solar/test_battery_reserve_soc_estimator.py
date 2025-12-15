from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

import pytest
from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


@pytest.fixture
def battery_reserve_soc_estimator(
    configuration: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_forecast_factory: Mock,
) -> BatteryReserveSocEstimator:
    configuration = replace(
        configuration,
        battery_capacity=EnergyKwh(10.0),
        battery_reserve_soc_min=BatterySoc(20.0),
        battery_reserve_soc_margin=BatterySoc(5.0),
        battery_reserve_soc_max=BatterySoc(100.0),
        night_low_tariff_time_start=time.fromisoformat("22:05:00"),
        night_low_tariff_time_end=time.fromisoformat("06:55:00"),
        day_low_tariff_time_start=time.fromisoformat("13:05:00"),
        day_low_tariff_time_end=time.fromisoformat("15:55:00"),
    )

    return BatteryReserveSocEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        configuration=configuration,
        forecast_factory=mock_forecast_factory,
    )


def test_estimate_soc_tomorrow_at_7_am_when_higher_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_reserve_soc=BatterySoc(50.0))

    now = datetime.fromisoformat("2025-10-10T22:05:00+00:00")
    high_tariff_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    hourly_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(2.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

    mock_production_forecast.hourly.assert_called_once_with(tomorrow_7_am, high_tariff_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(tomorrow_7_am, high_tariff_hours)

    # 4.0 kWh deficit (40%) + 20% min + 5% margin = 65%
    assert battery_reserve_soc == BatterySoc(65.0)


def test_estimate_soc_tomorrow_at_7_am_when_lower_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_reserve_soc=BatterySoc(50.0))

    now = datetime.fromisoformat("2025-10-10T22:05:00+00:00")
    high_tariff_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    hourly_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(5.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(6.0)),
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

    mock_production_forecast.hourly.assert_called_once_with(tomorrow_7_am, high_tariff_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(tomorrow_7_am, high_tariff_hours)

    # 1.0 kWh deficit (10%) + 20% min + 5% margin = 35%
    assert battery_reserve_soc == BatterySoc(35.0)


def test_estimate_soc_today_at_4_pm_when_grid_charging_needed(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(40.0), battery_reserve_soc=BatterySoc(20.0))

    now = datetime.fromisoformat("2025-10-10T15:00:00+00:00")

    today_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")

    afternoon_period = HourlyPeriod(now)
    evening_period = HourlyPeriod(today_4_pm)

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(1.0))],
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(6.0))],
    ]
    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(1.5))],
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(0.5))],
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

    # Evening deficit: 6.0 kWh - 0.5 kWh = 5.5 kWh
    # Afternoon surplus: 1.5 kWh - 1.0 kWh = 0.5 kWh
    # Net deficit (after solar): 5.5 kWh - 0.5 kWh = 5.0 kWh
    # Required SoC from battery: 5.0 kWh / 10.0 kWh = 50% + 20% min + 5% margin = 75%
    assert battery_reserve_soc == BatterySoc(75.0)


def test_estimate_soc_today_at_4_pm_when_reserve_soc_already_above_target(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(40.0), battery_reserve_soc=BatterySoc(80.0))

    now = datetime.fromisoformat("2025-10-10T15:00:00+00:00")

    today_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")

    afternoon_period = HourlyPeriod(now)
    evening_period = HourlyPeriod(today_4_pm)

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(1.0))],
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(6.0))],
    ]
    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(1.5))],
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(0.5))],
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

    # Battery reserve SoC (80%) is already above the target (75%)
    assert battery_reserve_soc is None


def test_estimate_soc_today_at_4_pm_when_solar_only_charging_sufficient(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(20.0), battery_reserve_soc=BatterySoc(20.0))

    now = datetime.fromisoformat("2025-10-10T15:00:00+00:00")

    today_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")

    afternoon_period = HourlyPeriod(now)
    evening_period = HourlyPeriod(today_4_pm)

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(1.0))],
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(6.0))],
    ]
    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(afternoon_period, energy=EnergyKwh(5.0))],
        [HourlyProductionEnergy(evening_period, energy=EnergyKwh(0.5))],
    ]

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

    # Evening deficit: 6.0 kWh - 0.5 kWh = 5.5 kWh
    # Afternoon surplus: 5.0 kWh - 1.0 kWh = 4.0 kWh
    # Net deficit (after solar): 5.5 kWh - 4.0 kWh = 1.5 kWh
    # SoC target: (1.5 kWh / 10.0 kWh) = 15% + 20% min + 5% margin = 40%
    # SoC solar only: 20% + (4.0 kWh / 10.0 kWh) = 20% + 40% = 60%
    # Since soc_solar_only (60%) >= soc_target (40%), no grid charging needed
    assert battery_reserve_soc is None
