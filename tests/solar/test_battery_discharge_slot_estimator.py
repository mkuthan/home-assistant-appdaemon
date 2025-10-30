from dataclasses import replace
from datetime import datetime, time
from decimal import Decimal
from unittest.mock import Mock

import pytest
from solar.battery_discharge_slot import BatteryDischargeSlot
from solar.battery_discharge_slot_estimator import BatteryDischargeSlotEstimator
from solar.price_forecast import HourlyPrice
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice
from units.hourly_energy import HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


@pytest.fixture
def battery_discharge_slot_estimator(
    configuration: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_forecast_factory: Mock,
) -> BatteryDischargeSlotEstimator:
    configuration = replace(
        configuration,
        battery_capacity=EnergyKwh(10.0),
        battery_voltage=BatteryVoltage(50.0),
        battery_maximum_current=BatteryCurrent(80.0),
        battery_reserve_soc_min=BatterySoc(20.0),
        battery_reserve_soc_margin=BatterySoc(5.0),
        battery_export_threshold_price=EnergyPrice.pln_per_mwh(Decimal(1200)),
        battery_export_threshold_energy=EnergyKwh(1.0),
    )

    return BatteryDischargeSlotEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        configuration=configuration,
        forecast_factory=mock_forecast_factory,
    )


def test_estimate_battery_discharge_at_4_pm_when_surplus_energy_for_two_slots(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(100.0))

    this_day = datetime.fromisoformat("2025-10-10T13:30:00+00:00")
    this_day_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    low_tariff_hours = 6

    hourly_period = HourlyPeriod(this_day_4_pm)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(2.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(4.0)),
    ]

    peak_period_1 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T19:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(1250)),
    )
    peak_period_2 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T20:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(1600)),
    )
    mock_price_forecast.find_peak_periods.return_value = [peak_period_1, peak_period_2]

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(state, this_day)

    mock_price_forecast.find_peak_periods.assert_called_once_with(
        this_day_4_pm,
        low_tariff_hours,
        battery_discharge_slot_estimator.configuration.battery_export_threshold_price,
    )
    mock_production_forecast.hourly.assert_called_once_with(this_day_4_pm, low_tariff_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(this_day_4_pm, low_tariff_hours)

    assert len(battery_discharge_slot) == 2
    assert battery_discharge_slot[0] == BatteryDischargeSlot(
        start_time=time(20, 0), end_time=time(21, 0), current=BatteryCurrent(80.00)
    )
    assert battery_discharge_slot[1] == BatteryDischargeSlot(
        start_time=time(19, 0), end_time=time(20, 0), current=BatteryCurrent(30.00)
    )


def test_estimate_battery_discharge_at_4_pm_when_surplus_energy_for_one_slot(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(90.0))

    this_day = datetime.fromisoformat("2025-10-10T13:30:00+00:00")
    this_day_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    low_tariff_hours = 6

    hourly_period = HourlyPeriod(this_day_4_pm)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(2.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(4.0)),
    ]

    peak_period_1 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T19:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(1250)),
    )
    peak_period_2 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T20:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(1600)),
    )
    mock_price_forecast.find_peak_periods.return_value = [peak_period_1, peak_period_2]

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(state, this_day)

    mock_price_forecast.find_peak_periods.assert_called_once_with(
        this_day_4_pm,
        low_tariff_hours,
        battery_discharge_slot_estimator.configuration.battery_export_threshold_price,
    )
    mock_production_forecast.hourly.assert_called_once_with(this_day_4_pm, low_tariff_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(this_day_4_pm, low_tariff_hours)

    assert len(battery_discharge_slot) == 1
    assert battery_discharge_slot[0] == BatteryDischargeSlot(
        start_time=time(20, 0), end_time=time(21, 0), current=BatteryCurrent(80.00)
    )


def test_estimate_battery_discharge_at_4_pm_when_surplus_energy_for_no_slots(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(50.0))

    this_day = datetime.fromisoformat("2025-10-10T13:30:00+00:00")
    this_day_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    low_tariff_hours = 6

    hourly_period = HourlyPeriod(this_day_4_pm)

    mock_production_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(2.0)),
    ]
    mock_consumption_forecast.hourly.return_value = [
        HourlyProductionEnergy(hourly_period, energy=EnergyKwh(4.0)),
    ]

    peak_period_1 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T19:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(1250)),
    )
    peak_period_2 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T20:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(1600)),
    )
    mock_price_forecast.find_peak_periods.return_value = [peak_period_1, peak_period_2]

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(state, this_day)

    mock_price_forecast.find_peak_periods.assert_called_once_with(
        this_day_4_pm,
        low_tariff_hours,
        battery_discharge_slot_estimator.configuration.battery_export_threshold_price,
    )
    mock_production_forecast.hourly.assert_called_once_with(this_day_4_pm, low_tariff_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(this_day_4_pm, low_tariff_hours)

    assert len(battery_discharge_slot) == 0


def test_estimate_battery_discharge_at_4_pm_when_no_peak_periods(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_price_forecast: Mock,
) -> None:
    mock_price_forecast.find_peak_periods.return_value = []

    this_day = datetime.fromisoformat("2025-10-10T13:30:00+00:00")
    this_day_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    low_tariff_hours = 6

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(state, this_day)

    mock_price_forecast.find_peak_periods.assert_called_once_with(
        this_day_4_pm,
        low_tariff_hours,
        battery_discharge_slot_estimator.configuration.battery_export_threshold_price,
    )

    assert len(battery_discharge_slot) == 0
