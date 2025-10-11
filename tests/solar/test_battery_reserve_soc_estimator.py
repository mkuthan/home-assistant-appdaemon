from dataclasses import replace
from datetime import datetime
from unittest.mock import Mock

from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh


def test_call_returns_estimated_reserve_soc_when_higher_than_current(
    mock_appdaemon_logger: Mock,
    config: SolarConfiguration,
    state: State,
) -> None:
    config = replace(
        config,
        battery_capacity=EnergyKwh(10.0),
        battery_reserve_soc_min=BatterySoc(20.0),
        battery_reserve_soc_margin=BatterySoc(5.0),
    )

    state = replace(state, battery_reserve_soc=BatterySoc(30.0))

    mock_production_forecast = Mock()
    mock_production_forecast.estimate_energy_kwh.return_value = EnergyKwh(2.0)

    mock_consumption_forecast = Mock()
    mock_consumption_forecast.estimate_energy_kwh.return_value = EnergyKwh(6.0)

    mock_forecast_factory = Mock()
    mock_forecast_factory.create_production_forecast.return_value = mock_production_forecast
    mock_forecast_factory.create_consumption_forecast.return_value = mock_consumption_forecast

    estimator = BatteryReserveSocEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        config=config,
        forecast_factory=mock_forecast_factory,
    )

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")

    battery_reserve_soc = estimator(state, period_start, period_hours=6)

    mock_production_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)
    mock_consumption_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)

    assert battery_reserve_soc == BatterySoc(65.0)
