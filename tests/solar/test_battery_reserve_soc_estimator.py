from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

import pytest
from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_soc import BATTERY_SOC_MAX, BatterySoc
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


@pytest.fixture
def battery_reserve_soc_estimator(
    configuration: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_sensor_publisher: Mock,
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
        sensor_publisher=mock_sensor_publisher,
        configuration=configuration,
        forecast_factory=mock_forecast_factory,
    )


def test_estimate_soc_tomorrow_at_7_am_when_higher_than_current(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_sensor_publisher: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(30.0), battery_reserve_soc=BatterySoc(50.0))

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

    mock_sensor_publisher.publish.assert_any_call(
        "battery_reserve_soc_7am",
        65.0,
        {
            "unit_of_measurement": "%",
            "window_start": tomorrow_7_am,
            "window_hours": high_tariff_hours,
            "consumption": EnergyKwh(6.0),
            "production": EnergyKwh(2.0),
            "energy_reserve": EnergyKwh(4.0),
            "battery_soc": BatterySoc(30.0),
            "battery_reserve_soc": BatterySoc(50.0),
            "estimated_at": now,
            "reason": "use target",
        },
    )

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

    # 1.0 kWh deficit (10%) + 20% min + 5% margin = 35% < 50%
    assert battery_reserve_soc is None


def test_estimate_soc_today_at_4_pm_when_grid_charging_needed(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_sensor_publisher: Mock,
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

    mock_sensor_publisher.publish.assert_any_call(
        "battery_reserve_soc_4pm",
        75.0,
        {
            "unit_of_measurement": "%",
            "window_start": today_4_pm,
            "window_hours": 6,
            "remaining_hours": 1,
            "remaining_consumption": EnergyKwh(1.0),
            "remaining_production": EnergyKwh(1.5),
            "evening_consumption": EnergyKwh(6.0),
            "evening_production": EnergyKwh(0.5),
            "energy_surplus": EnergyKwh(0.5),
            "evening_deficit": EnergyKwh(5.5),
            "energy_reserve": EnergyKwh(5.0),
            "battery_soc_solar_only": BatterySoc(45.0),
            "battery_soc": BatterySoc(40.0),
            "battery_reserve_soc": BatterySoc(20.0),
            "estimated_at": now,
            "reason": "use target",
        },
    )

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


def test_estimate_soc_timer_idle_in_low_tariff_forces_battery_soc_max(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_forecast_factory: Mock,
    mock_sensor_publisher: Mock,
) -> None:
    state = replace(
        state,
        battery_full_charge_timer_state="idle",
        battery_reserve_soc=BatterySoc(90.0),
    )

    now = datetime.fromisoformat("2025-10-10T22:05:00+00:00")

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

    assert battery_reserve_soc == BATTERY_SOC_MAX
    mock_sensor_publisher.publish.assert_called_once_with(
        "battery_reserve_soc",
        100.0,
        {
            "unit_of_measurement": "%",
            "tariff": "full_charge",
            "battery_full_charge_timer_state": "idle",
            "battery_reserve_soc": BatterySoc(90.0),
            "changed": True,
            "estimated_at": now,
        },
    )
    mock_forecast_factory.create_consumption_forecast.assert_not_called()
    mock_forecast_factory.create_production_forecast.assert_not_called()


def test_estimate_soc_timer_idle_outside_low_tariff_uses_default_minimum(
    battery_reserve_soc_estimator: BatteryReserveSocEstimator,
    state: SolarState,
    mock_forecast_factory: Mock,
    mock_sensor_publisher: Mock,
) -> None:
    state = replace(
        state,
        battery_full_charge_timer_state="idle",
        battery_reserve_soc=BatterySoc(30.0),
    )

    now = datetime.fromisoformat("2025-10-10T10:00:00+00:00")

    battery_reserve_soc = battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

    assert battery_reserve_soc == BatterySoc(20.0)
    mock_sensor_publisher.publish.assert_called_once_with(
        "battery_reserve_soc",
        20.0,
        {
            "unit_of_measurement": "%",
            "tariff": "high",
            "battery_full_charge_timer_state": "idle",
            "battery_reserve_soc": BatterySoc(30.0),
            "changed": True,
            "estimated_at": now,
        },
    )
    mock_forecast_factory.create_consumption_forecast.assert_not_called()
    mock_forecast_factory.create_production_forecast.assert_not_called()
