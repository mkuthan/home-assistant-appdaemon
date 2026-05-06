from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.storage_mode import StorageMode
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod
from units.hourly_price import HourlyPrice
from units.money import Money


@pytest.fixture
def storage_mode_estimator(
    configuration: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_forecast_factory: Mock,
) -> StorageModeEstimator:
    configuration = replace(
        configuration,
        battery_capacity=EnergyKwh(10.0),
        battery_reserve_soc_min=BatterySoc(20.0),
        battery_reserve_soc_margin=BatterySoc(5.0),
        pv_export_threshold_price=EnergyPrice.per_mwh(Money.pln(Decimal(200))),
    )

    return StorageModeEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        configuration=configuration,
        forecast_factory=mock_forecast_factory,
    )


@pytest.fixture
def any_hourly_period() -> HourlyPeriod:
    return HourlyPeriod(datetime.fromisoformat("2025-10-10T12:00:00+00:00"))


@pytest.fixture
def any_hourly_price(any_hourly_period: HourlyPeriod) -> HourlyPrice:
    return HourlyPrice(any_hourly_period, EnergyPrice.per_mwh(Money.pln(Decimal(0))))


def test_estimator_self_use_when_no_remaining_hours(
    storage_mode_estimator: StorageModeEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, inverter_storage_mode=StorageMode.FEED_IN_PRIORITY)

    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    storage_mode = storage_mode_estimator.estimate_storage_mode(state, now)

    mock_production_forecast.hourly.assert_not_called()
    mock_consumption_forecast.hourly.assert_not_called()
    mock_price_forecast.find_min_hour.assert_not_called()

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_self_use_when_battery_soc_below_reserve(
    storage_mode_estimator: StorageModeEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(
        state,
        inverter_storage_mode=StorageMode.FEED_IN_PRIORITY,
        battery_soc=BatterySoc(22.0),
    )

    now = datetime.fromisoformat("2025-10-10T10:00:00+00:00")

    storage_mode = storage_mode_estimator.estimate_storage_mode(state, now)

    mock_production_forecast.hourly.assert_not_called()
    mock_consumption_forecast.hourly.assert_not_called()
    mock_price_forecast.find_min_hour.assert_not_called()

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_self_use_when_min_price_not_found(
    storage_mode_estimator: StorageModeEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(
        state,
        inverter_storage_mode=StorageMode.FEED_IN_PRIORITY,
        battery_soc=BatterySoc(80.0),
    )

    mock_price_forecast.find_min_hour.return_value = None

    now = datetime.fromisoformat("2025-10-10T10:00:00+00:00")

    today_8_am = datetime.fromisoformat("2025-10-10T08:00:00+00:00")
    day_hours = 8

    storage_mode = storage_mode_estimator.estimate_storage_mode(state, now)

    mock_production_forecast.hourly.assert_not_called()
    mock_consumption_forecast.hourly.assert_not_called()
    mock_price_forecast.find_min_hour.assert_called_once_with(today_8_am, day_hours)

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_self_use_when_current_price_below_threshold(
    storage_mode_estimator: StorageModeEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
    any_hourly_price: HourlyPrice,
) -> None:
    state = replace(
        state,
        inverter_storage_mode=StorageMode.FEED_IN_PRIORITY,
        battery_soc=BatterySoc(80.0),
        hourly_price=EnergyPrice.per_mwh(Money.pln(Decimal(150))),
    )

    now = datetime.fromisoformat("2025-10-10T10:00:00+00:00")

    today_8_am = datetime.fromisoformat("2025-10-10T08:00:00+00:00")
    day_hours = 8

    mock_price_forecast.find_min_hour.return_value = any_hourly_price

    storage_mode = storage_mode_estimator.estimate_storage_mode(state, now)

    mock_production_forecast.hourly.assert_not_called()
    mock_consumption_forecast.hourly.assert_not_called()
    mock_price_forecast.find_min_hour.assert_called_once_with(today_8_am, day_hours)

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_self_use_when_no_enough_surplus_energy(
    storage_mode_estimator: StorageModeEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
    any_hourly_price: HourlyPrice,
) -> None:
    state = replace(
        state,
        inverter_storage_mode=StorageMode.FEED_IN_PRIORITY,
        battery_soc=BatterySoc(80.0),
        hourly_price=EnergyPrice.per_mwh(Money.pln(Decimal(250))),
    )

    now = datetime.fromisoformat("2025-10-10T10:00:00+00:00")
    remaining_hours = 15 - now.hour
    today_8_am = datetime.fromisoformat("2025-10-10T08:00:00+00:00")
    day_hours = 8

    mock_price_forecast.find_min_hour.return_value = any_hourly_price

    hourly_period = HourlyPeriod(now)

    mock_production_forecast.hourly.return_value = [HourlyProductionEnergy(hourly_period, EnergyKwh(5.0))]
    mock_consumption_forecast.hourly.return_value = [HourlyConsumptionEnergy(hourly_period, EnergyKwh(6.0))]

    storage_mode = storage_mode_estimator.estimate_storage_mode(state, now)

    mock_production_forecast.hourly.assert_called_once_with(now, remaining_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(now, remaining_hours)
    mock_price_forecast.find_min_hour.assert_called_once_with(today_8_am, day_hours)

    assert storage_mode == StorageMode.SELF_USE


def test_estimator_feed_in_priority(
    storage_mode_estimator: StorageModeEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
    any_hourly_price: HourlyPrice,
) -> None:
    state = replace(
        state,
        inverter_storage_mode=StorageMode.SELF_USE,
        battery_soc=BatterySoc(80.0),
        hourly_price=EnergyPrice.per_mwh(Money.pln(Decimal(250))),
    )

    now = datetime.fromisoformat("2025-10-10T10:00:00+00:00")
    remaining_hours = 15 - now.hour

    today_8_am = datetime.fromisoformat("2025-10-10T08:00:00+00:00")
    day_hours = 8

    mock_price_forecast.find_min_hour.return_value = any_hourly_price

    hourly_period = HourlyPeriod(now)

    mock_production_forecast.hourly.return_value = [HourlyProductionEnergy(hourly_period, EnergyKwh(8.0))]
    mock_consumption_forecast.hourly.return_value = [HourlyConsumptionEnergy(hourly_period, EnergyKwh(4.0))]

    storage_mode = storage_mode_estimator.estimate_storage_mode(state, now)

    mock_production_forecast.hourly.assert_called_once_with(now, remaining_hours)
    mock_consumption_forecast.hourly.assert_called_once_with(now, remaining_hours)
    mock_price_forecast.find_min_hour.assert_called_once_with(today_8_am, day_hours)

    assert storage_mode == StorageMode.FEED_IN_PRIORITY


def test_estimator_skip_when_storage_mode_unchanged(
    storage_mode_estimator: StorageModeEstimator,
    state: SolarState,
) -> None:
    state = replace(state, inverter_storage_mode=StorageMode.SELF_USE)

    now = datetime.fromisoformat("2025-10-10T13:00:00+00:00")

    storage_mode = storage_mode_estimator.estimate_storage_mode(state, now)

    assert storage_mode is None
