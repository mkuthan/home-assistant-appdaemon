from dataclasses import replace
from datetime import datetime
from unittest.mock import ANY, Mock

import pytest
from entities.entities import COOLING_ENTITY, DHW_ENTITY, HEATING_ENTITY
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
def mock_heating_estimator() -> Mock:
    return Mock()


@pytest.fixture
def mock_cooling_estimator() -> Mock:
    return Mock()


@pytest.fixture
def hvac(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_service: Mock,
    configuration: HvacConfiguration,
    mock_state_factory: Mock,
    mock_dhw_estimator: Mock,
    mock_heating_estimator: Mock,
    mock_cooling_estimator: Mock,
) -> Hvac:
    return Hvac(
        mock_appdaemon_logger,
        mock_appdaemon_service,
        configuration,
        mock_state_factory,
        mock_dhw_estimator,
        mock_heating_estimator,
        mock_cooling_estimator,
    )


def test_control(
    hvac: Hvac,
    state: HvacState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_dhw_estimator: Mock,
    mock_heating_estimator: Mock,
    mock_cooling_estimator: Mock,
) -> None:
    current_dhw_temperature = Celsius(35.0)
    new_dhw_temperature = Celsius(45.0)

    current_heating_temperature = Celsius(20.0)
    new_heating_temperature = Celsius(22.0)

    current_cooling_temperature = Celsius(26.0)
    new_cooling_temperature = Celsius(24.0)

    state = replace(
        state,
        dhw_temperature=current_dhw_temperature,
        heating_temperature=current_heating_temperature,
        cooling_temperature=current_cooling_temperature,
    )
    mock_state_factory.create.return_value = state

    mock_dhw_estimator.estimate_temperature.return_value = new_dhw_temperature
    mock_heating_estimator.estimate_temperature.return_value = new_heating_temperature
    mock_cooling_estimator.estimate_temperature.return_value = new_cooling_temperature

    now = datetime.now()
    hvac.control(now)

    mock_dhw_estimator.estimate_temperature.assert_called_once_with(state, now)
    mock_heating_estimator.estimate_temperature.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_any_call(
        "water_heater/set_temperature",
        callback=ANY,
        entity_id=DHW_ENTITY,
        temperature=new_dhw_temperature.value,
    )

    mock_appdaemon_service.call_service.assert_any_call(
        "climate/set_temperature",
        callback=ANY,
        entity_id=HEATING_ENTITY,
        temperature=new_heating_temperature.value,
    )

    mock_appdaemon_service.call_service.assert_any_call(
        "climate/set_temperature",
        callback=ANY,
        entity_id=COOLING_ENTITY,
        temperature=new_cooling_temperature.value,
    )


def test_control_no_change(
    hvac: Hvac,
    state: HvacState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_dhw_estimator: Mock,
    mock_heating_estimator: Mock,
    mock_cooling_estimator: Mock,
) -> None:
    current_dhw_temperature = Celsius(35.0)
    current_heating_temperature = Celsius(20.0)
    current_cooling_temperature = Celsius(26.0)

    state = replace(
        state,
        dhw_temperature=current_dhw_temperature,
        heating_temperature=current_heating_temperature,
        cooling_temperature=current_cooling_temperature,
    )
    mock_state_factory.create.return_value = state

    mock_dhw_estimator.estimate_temperature.return_value = None
    mock_heating_estimator.estimate_temperature.return_value = None
    mock_cooling_estimator.estimate_temperature.return_value = None

    now = datetime.now()
    hvac.control(now)

    mock_dhw_estimator.estimate_temperature.assert_called_once_with(state, now)
    mock_heating_estimator.estimate_temperature.assert_called_once_with(state, now)
    mock_cooling_estimator.estimate_temperature.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_not_called()
