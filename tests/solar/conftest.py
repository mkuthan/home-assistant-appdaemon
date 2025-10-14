from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_production_forecast() -> Mock:
    return Mock()


@pytest.fixture
def mock_consumption_forecast() -> Mock:
    return Mock()


@pytest.fixture
def mock_price_forecast() -> Mock:
    return Mock()


@pytest.fixture
def mock_forecast_factory(
    mock_production_forecast: Mock, mock_consumption_forecast: Mock, mock_price_forecast: Mock
) -> Mock:
    mock_forecast_factory = Mock()
    mock_forecast_factory.create_production_forecast.return_value = mock_production_forecast
    mock_forecast_factory.create_consumption_forecast.return_value = mock_consumption_forecast
    mock_forecast_factory.create_price_forecast.return_value = mock_price_forecast

    return mock_forecast_factory
