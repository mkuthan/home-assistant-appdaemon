from unittest.mock import Mock

import pytest
from solar.consumption_forecast import ConsumptionForecastComposite
from solar.forecast_factory import DefaultForecastFactory
from solar.price_forecast import PriceForecast
from solar.production_forecast import ProductionForecastComposite
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.weather_forecast import WeatherForecast


@pytest.fixture
def forecast_factory(mock_appdaemon_logger: Mock, configuration: SolarConfiguration) -> DefaultForecastFactory:
    return DefaultForecastFactory(appdaemon_logger=mock_appdaemon_logger, configuration=configuration)


def test_create_production_forecast(
    forecast_factory: DefaultForecastFactory,
    state: SolarState,
) -> None:
    production_forecast = forecast_factory.create_production_forecast(state)

    assert isinstance(production_forecast, ProductionForecastComposite)
    assert len(production_forecast.components) == 2


def test_create_consumption_forecast(
    forecast_factory: DefaultForecastFactory,
    state: SolarState,
) -> None:
    consumption_forecast = forecast_factory.create_consumption_forecast(state)

    assert isinstance(consumption_forecast, ConsumptionForecastComposite)
    assert len(consumption_forecast.components) == 2


def test_create_price_forecast(
    forecast_factory: DefaultForecastFactory,
    state: SolarState,
) -> None:
    price_forecast = forecast_factory.create_price_forecast(state)

    assert isinstance(price_forecast, PriceForecast)


def test_create_weather_forecast(
    forecast_factory: DefaultForecastFactory,
    state: SolarState,
) -> None:
    weather_forecast = forecast_factory.create_weather_forecast(state)

    assert isinstance(weather_forecast, WeatherForecast)
