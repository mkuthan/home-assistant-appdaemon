from dataclasses import replace
from datetime import datetime
from unittest.mock import Mock

import pytest
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from solar.storage_mode import StorageMode
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice


@pytest.fixture
def storage_mode_estimator(
    config: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_forecast_factory: Mock,
) -> StorageModeEstimator:
    config = replace(
        config,
        battery_capacity=EnergyKwh(10.0),
        battery_reserve_soc_min=BatterySoc(20.0),
        pv_export_min_price_margin=EnergyPrice.pln_per_mwh(200.0),
    )

    return StorageModeEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        config=config,
        forecast_factory=mock_forecast_factory,
    )


def test_call_returns_feed_in_priority(
    storage_mode_estimator: StorageModeEstimator,
    state: State,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(80.0), hourly_price=EnergyPrice.pln_per_mwh(250.0))

    mock_production_forecast.estimate_energy_kwh.return_value = EnergyKwh(8.0)
    mock_consumption_forecast.estimate_energy_kwh.return_value = EnergyKwh(6.0)
    mock_price_forecast.find_daily_min_price.return_value = EnergyPrice.pln_per_mwh(30.0)

    period_start = datetime.now()

    storage_mode = storage_mode_estimator(state, period_start, 6)

    mock_production_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)
    mock_consumption_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)
    mock_price_forecast.find_daily_min_price.assert_called_once_with(period_start, 6)

    assert storage_mode == StorageMode.FEED_IN_PRIORITY
