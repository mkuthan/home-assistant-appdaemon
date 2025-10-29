from dataclasses import replace
from datetime import datetime
from unittest.mock import Mock

import pytest
from hvac.hvac import Hvac
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import Celsius


@pytest.fixture
def mock_state_factory() -> Mock:
    return Mock()


@pytest.fixture
def mock_dhw_estimator() -> Mock:
    return Mock()


@pytest.fixture
def hvac(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_service: Mock,
    configuration: HvacConfiguration,
    mock_state_factory: Mock,
    mock_dhw_estimator: Mock,
) -> Hvac:
    return Hvac(
        mock_appdaemon_logger,
        mock_appdaemon_service,
        configuration,
        mock_state_factory,
        mock_dhw_estimator,
    )


def test_control(
    hvac: Hvac,
    state: HvacState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_dhw_estimator: Mock,
) -> None:
    current_dhw_temperature = Celsius(35.0)
    new_dhw_temperature = Celsius(45.0)

    state = replace(state, dhw_temperature=current_dhw_temperature)
    mock_state_factory.create.return_value = state

    mock_dhw_estimator.estimate_temperature.return_value = new_dhw_temperature

    now = datetime.now()
    hvac.control(now)

    mock_dhw_estimator.estimate_temperature.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_called_once_with(
        "water_heater.set_temperature",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="water_heater.panasonic_heat_pump_main_dhw_target_temp",
        value=new_dhw_temperature.value,
    )
