from dataclasses import replace
from datetime import datetime
from unittest.mock import Mock

from solar.solar_configuration import SolarConfiguration
from solar.state import State
from solar.storage_mode import StorageMode
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice


def test_call_returns_feed_in_priority(
    mock_appdaemon_logger: Mock,
    config: SolarConfiguration,
    state: State,
) -> None:
    config = replace(
        config, battery_capacity=EnergyKwh(10.0), pv_export_min_price_margin=EnergyPrice.pln_per_mwh(200.0)
    )
    state = replace(state, battery_soc=BatterySoc(80.0), hourly_price=EnergyPrice.pln_per_mwh(250.0))

    mock_production_forecast = Mock()
    mock_production_forecast.estimate_energy_kwh.return_value = EnergyKwh(8.0)

    mock_consumption_forecast = Mock()
    mock_consumption_forecast.estimate_energy_kwh.return_value = EnergyKwh(6.0)

    mock_price_forecast = Mock()
    mock_price_forecast.find_daily_min_price.return_value = EnergyPrice.pln_per_mwh(30.0)

    mock_forecast_factory = Mock()
    mock_forecast_factory.create_production_forecast.return_value = mock_production_forecast
    mock_forecast_factory.create_consumption_forecast.return_value = mock_consumption_forecast
    mock_forecast_factory.create_price_forecast.return_value = mock_price_forecast

    estimator = StorageModeEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        config=config,
        forecast_factory=mock_forecast_factory,
    )

    period_start = datetime.now()

    storage_mode = estimator(state, period_start, 6)

    mock_production_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)
    mock_consumption_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)
    mock_price_forecast.find_daily_min_price.assert_called_once_with(period_start, 6)

    assert storage_mode == StorageMode.FEED_IN_PRIORITY
