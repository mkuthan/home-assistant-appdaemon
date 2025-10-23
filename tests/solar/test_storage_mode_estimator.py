from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from solar.storage_mode import StorageMode
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


@pytest.fixture
def storage_mode_estimator(
    config: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_forecast_factory: Mock,
) -> StorageModeEstimator:
    config = replace(
        config,
        battery_capacity=EnergyKwh(10.0),
        battery_reserve_soc_min=BatterySoc(value=Decimal("20.0")),
        pv_export_min_price_margin=EnergyPrice.pln_per_mwh(200.0),
    )

    return StorageModeEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        config=config,
        forecast_factory=mock_forecast_factory,
    )


def test_estimator_feed_in_priority(
    storage_mode_estimator: StorageModeEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(value=Decimal("80.0")), hourly_price=EnergyPrice.pln_per_mwh(250.0))

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    period_hours = 6

    hourly_period = HourlyPeriod.parse("2025-10-10T16:00:00+00:00")

    mock_production_forecast.hourly.return_value = [HourlyProductionEnergy(hourly_period, EnergyKwh(8.0))]
    mock_consumption_forecast.hourly.return_value = [HourlyConsumptionEnergy(hourly_period, EnergyKwh(6.0))]
    mock_price_forecast.find_daily_min_price.return_value = EnergyPrice.pln_per_mwh(30.0)

    storage_mode = storage_mode_estimator(state, period_start, period_hours)

    mock_production_forecast.hourly.assert_called_once_with(period_start, period_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(period_start, period_hours)
    mock_price_forecast.find_daily_min_price.assert_called_once_with(period_start, period_hours)

    assert storage_mode == StorageMode.FEED_IN_PRIORITY


def test_estimator_self_use_when_battery_soc_below_reserve(
    storage_mode_estimator: StorageModeEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(value=Decimal("20.0")), hourly_price=EnergyPrice.pln_per_mwh(250.0))

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    period_hours = 6

    storage_mode = storage_mode_estimator(state, period_start, period_hours)

    mock_production_forecast.hourly.assert_not_called()
    mock_consumption_forecast.hourly.assert_not_called()
    mock_price_forecast.find_daily_min_price.assert_not_called()

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_self_use_when_min_price_not_found(
    storage_mode_estimator: StorageModeEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(value=Decimal("80.0")), hourly_price=EnergyPrice.pln_per_mwh(250.0))

    mock_price_forecast.find_daily_min_price.return_value = None

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    period_hours = 6

    storage_mode = storage_mode_estimator(state, period_start, period_hours)

    mock_production_forecast.hourly.assert_not_called()
    mock_consumption_forecast.hourly.assert_not_called()
    mock_price_forecast.find_daily_min_price.assert_called_once_with(period_start, period_hours)

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_self_use_when_current_price_below_threshold(
    storage_mode_estimator: StorageModeEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(value=Decimal("80.0")), hourly_price=EnergyPrice.pln_per_mwh(150.0))

    mock_price_forecast.find_daily_min_price.return_value = EnergyPrice.pln_per_mwh(30.0)

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    period_hours = 6

    storage_mode = storage_mode_estimator(state, period_start, period_hours)

    mock_production_forecast.hourly.assert_not_called()
    mock_consumption_forecast.hourly.assert_not_called()
    mock_price_forecast.find_daily_min_price.assert_called_once_with(period_start, period_hours)

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_self_use_when_no_enough_surplus_energy(
    storage_mode_estimator: StorageModeEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(value=Decimal("80.0")), hourly_price=EnergyPrice.pln_per_mwh(250.0))

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    period_hours = 6

    hourly_period = HourlyPeriod.parse("2025-10-10T16:00:00+00:00")

    mock_production_forecast.hourly.return_value = [HourlyProductionEnergy(hourly_period, EnergyKwh(5.0))]
    mock_consumption_forecast.hourly.return_value = [HourlyConsumptionEnergy(hourly_period, EnergyKwh(6.0))]
    mock_price_forecast.find_daily_min_price.return_value = EnergyPrice.pln_per_mwh(30.0)

    storage_mode = storage_mode_estimator(state, period_start, period_hours)

    mock_production_forecast.hourly.assert_called_once_with(period_start, period_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(period_start, period_hours)
    mock_price_forecast.find_daily_min_price.assert_called_once_with(period_start, period_hours)

    assert storage_mode == StorageMode.SELF_USE
