import logging
from unittest.mock import Mock

import pytest
from entities.entities import (
    COOLING_ENTITY,
    DHW_ENTITY,
    DHW_TEMPERATURE_ENTITY,
    ECO_MODE_ENTITY,
    HEATING_CURVE_TARGET_HIGH_TEMP_ENTITY,
    HEATING_CURVE_TARGET_LOW_TEMP_ENTITY,
    HEATING_ENTITY,
    INDOOR_TEMPERATURE_ENTITY,
    TEMPERATURE_ADJUSTMENT_ENTITY,
)
from hvac.hvac_state_factory import DefaultHvacStateFactory
from units.celsius import Celsius


@pytest.fixture
def state_values() -> dict:
    return {
        f"{ECO_MODE_ENTITY}:": "off",
        f"{DHW_TEMPERATURE_ENTITY}:": "35.0",
        f"{DHW_ENTITY}:temperature": "40.0",
        f"{INDOOR_TEMPERATURE_ENTITY}:": "20.0",
        f"{HEATING_ENTITY}:temperature": "21",
        f"{HEATING_ENTITY}:": "heat",
        f"{COOLING_ENTITY}:temperature": "24",
        f"{COOLING_ENTITY}:": "cool",
        f"{HEATING_CURVE_TARGET_HIGH_TEMP_ENTITY}:": "28.0",
        f"{HEATING_CURVE_TARGET_LOW_TEMP_ENTITY}:": "24.0",
        f"{TEMPERATURE_ADJUSTMENT_ENTITY}:": "0.0",
    }


def test_create(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    state_values: dict,
) -> None:
    mock_appdaemon_state.get_state.side_effect = lambda entity_id, attribute="", *_args, **_kwargs: state_values.get(
        f"{entity_id}:{attribute}"
    )

    result = DefaultHvacStateFactory(mock_appdaemon_logger, mock_appdaemon_state).create()

    assert result is not None
    assert result.is_eco_mode is False
    assert result.dhw_actual_temperature == Celsius(35.0)
    assert result.dhw_target_temperature == Celsius(40.0)
    assert result.indoor_actual_temperature == Celsius(20.0)
    assert result.heating_target_temperature == Celsius(21.0)
    assert result.heating_mode == "heat"
    assert result.cooling_target_temperature == Celsius(24.0)
    assert result.cooling_mode == "cool"
    assert result.heating_curve_target_high_temp == Celsius(28.0)
    assert result.heating_curve_target_low_temp == Celsius(24.0)
    assert result.temperature_adjustment == Celsius(0.0)


@pytest.mark.parametrize(
    ("missing_entity", "expected_message"),
    [
        (f"{ECO_MODE_ENTITY}:", "Can't create state, missing: is_eco_mode"),
        (f"{DHW_TEMPERATURE_ENTITY}:", "Can't create state, missing: dhw_actual_temperature"),
        (f"{DHW_ENTITY}:temperature", "Can't create state, missing: dhw_target_temperature"),
        (f"{INDOOR_TEMPERATURE_ENTITY}:", "Can't create state, missing: indoor_actual_temperature"),
        (f"{HEATING_ENTITY}:temperature", "Can't create state, missing: heating_target_temperature"),
        (f"{HEATING_ENTITY}:", "Can't create state, missing: heating_mode"),
        (f"{COOLING_ENTITY}:temperature", "Can't create state, missing: cooling_target_temperature"),
        (f"{COOLING_ENTITY}:", "Can't create state, missing: cooling_mode"),
        (f"{HEATING_CURVE_TARGET_HIGH_TEMP_ENTITY}:", "Can't create state, missing: heating_curve_target_high_temp"),
        (f"{HEATING_CURVE_TARGET_LOW_TEMP_ENTITY}:", "Can't create state, missing: heating_curve_target_low_temp"),
        (f"{TEMPERATURE_ADJUSTMENT_ENTITY}:", "Can't create state, missing: temperature_adjustment"),
    ],
)
def test_create_missing_field(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    state_values: dict,
    missing_entity: str,
    expected_message: str,
) -> None:
    mock_appdaemon_state.get_state.side_effect = (
        lambda entity_id, attribute="", *_args, **_kwargs: state_values.get(f"{entity_id}:{attribute}")
        if f"{entity_id}:{attribute}" != missing_entity
        else None
    )

    result = DefaultHvacStateFactory(mock_appdaemon_logger, mock_appdaemon_state).create()

    assert result is None
    mock_appdaemon_logger.log.assert_called_once_with(expected_message, level=logging.WARNING)
