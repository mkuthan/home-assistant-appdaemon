from unittest.mock import Mock

import pytest
from hvac.hvac import Hvac
from hvac.hvac_configuration import HvacConfiguration


@pytest.fixture
def mock_state_factory() -> Mock:
    return Mock()


@pytest.fixture
def hvac(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_service: Mock,
    config: HvacConfiguration,
    mock_state_factory: Mock,
) -> Hvac:
    return Hvac(
        mock_appdaemon_logger,
        mock_appdaemon_service,
        config,
        mock_state_factory,
    )
