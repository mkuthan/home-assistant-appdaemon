from unittest.mock import Mock

import pytest
from entities.entities import COOLING_ENTITY, DHW_ENTITY, ECO_MODE_ENTITY, HEATING_ENTITY
from hvac.hvac_state_factory import DefaultHvacStateFactory
from units.celsius import Celsius


@pytest.fixture
def state_values() -> dict:
    return {
        f"{ECO_MODE_ENTITY}:": "off",
        f"{DHW_ENTITY}:temperature": "40.0",
        f"{HEATING_ENTITY}:temperature": "21",
        f"{HEATING_ENTITY}:": "heat",
        f"{COOLING_ENTITY}:temperature": "24",
        f"{COOLING_ENTITY}:": "cool",
    }


def test_create(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    mock_appdaemon_service: Mock,
    state_values: dict,
) -> None:
    mock_appdaemon_state.get_state.side_effect = lambda entity_id, attribute="", *_args, **_kwargs: state_values.get(
        f"{entity_id}:{attribute}"
    )

    result = DefaultHvacStateFactory(mock_appdaemon_logger, mock_appdaemon_state, mock_appdaemon_service).create()

    assert result is not None
    assert result.is_eco_mode is False
    assert result.dhw_temperature == Celsius(40.0)
    assert result.heating_temperature == Celsius(21.0)
    assert result.heating_mode == "heat"
    assert result.cooling_temperature == Celsius(24.0)
    assert result.cooling_mode == "cool"


@pytest.mark.parametrize(
    ("missing_entity_or_service", "expected_message"),
    [
        (f"{ECO_MODE_ENTITY}:", "Missing: is_eco_mode"),
        (f"{DHW_ENTITY}:temperature", "Missing: dhw_temperature"),
        (f"{HEATING_ENTITY}:temperature", "Missing: heating_temperature"),
        (f"{HEATING_ENTITY}:", "Missing: heating_mode"),
        (f"{COOLING_ENTITY}:temperature", "Missing: cooling_temperature"),
        (f"{COOLING_ENTITY}:", "Missing: cooling_mode"),
    ],
)
def test_create_missing_field(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    mock_appdaemon_service: Mock,
    state_values: dict,
    missing_entity_or_service: str,
    expected_message: str,
) -> None:
    mock_appdaemon_state.get_state.side_effect = (
        lambda entity_id, attribute="", *_args, **_kwargs: state_values.get(f"{entity_id}:{attribute}")
        if f"{entity_id}:{attribute}" != missing_entity_or_service
        else None
    )

    result = DefaultHvacStateFactory(mock_appdaemon_logger, mock_appdaemon_state, mock_appdaemon_service).create()

    assert result is None
    mock_appdaemon_logger.warn.assert_called_once_with(expected_message)
