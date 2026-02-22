import logging
from decimal import Decimal
from unittest.mock import Mock

import pytest
from entities.entities import (
    AWAY_MODE_ENTITY,
    BATTERY_MAX_CHARGE_CURRENT_ENTITY,
    BATTERY_MAX_DISCHARGE_CURRENT_ENTITY,
    BATTERY_RESERVE_SOC_ENTITY,
    BATTERY_SOC_ENTITY,
    ECO_MODE_ENTITY,
    HEATING_ENTITY,
    INDOOR_TEMPERATURE_ENTITY,
    INVERTER_STORAGE_MODE_ENTITY,
    OUTDOOR_TEMPERATURE_ENTITY,
    PRICE_FORECAST_ENTITY,
    PV_FORECAST_TODAY_ENTITY,
    PV_FORECAST_TOMORROW_ENTITY,
    SLOT1_DISCHARGE_CURRENT_ENTITY,
    SLOT1_DISCHARGE_ENABLED_ENTITY,
    SLOT1_DISCHARGE_TIME_ENTITY,
    WEATHER_FORECAST_ENTITY,
)
from solar.solar_state_factory import DefaultSolarStateFactory
from solar.storage_mode import StorageMode
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.celsius import Celsius
from units.energy_price import EnergyPrice


@pytest.fixture
def pv_forecast_today() -> list[dict]:
    return [
        {"period_start": "2025-10-05T06:00:00+00:00", "pv_estimate": 1.0},
    ]


@pytest.fixture
def pv_forecast_tomorrow() -> list[dict]:
    return [
        {"period_start": "2025-10-06T06:00:00+00:00", "pv_estimate": 1.2},
    ]


@pytest.fixture
def weather_forecast() -> list[dict]:
    return [
        {"datetime": "2025-10-05T14:00:00+00:00", "temperature": 12.0, "humidity": 46.0},
    ]


@pytest.fixture
def price_forecast() -> list[dict]:
    return [
        {"dtime": "2025-10-03T16:00:00+00:00", "rce_pln": 426.1},
    ]


@pytest.fixture
def state_values(
    pv_forecast_today: list[dict],
    pv_forecast_tomorrow: list[dict],
    weather_forecast: list[dict],
    price_forecast: list[dict],
) -> dict:
    return {
        f"{BATTERY_SOC_ENTITY}:": "75.5",
        f"{BATTERY_RESERVE_SOC_ENTITY}:": "20.0",
        f"{BATTERY_MAX_CHARGE_CURRENT_ENTITY}:": "50.0",
        f"{BATTERY_MAX_DISCHARGE_CURRENT_ENTITY}:": "50.0",
        f"{INDOOR_TEMPERATURE_ENTITY}:": "21.5",
        f"{OUTDOOR_TEMPERATURE_ENTITY}:": "10.0",
        f"{AWAY_MODE_ENTITY}:": "off",
        f"{ECO_MODE_ENTITY}:": "on",
        f"{INVERTER_STORAGE_MODE_ENTITY}:": "Self-Use",
        f"{SLOT1_DISCHARGE_ENABLED_ENTITY}:": "on",
        f"{SLOT1_DISCHARGE_TIME_ENTITY}:": "19:00-20:00",
        f"{SLOT1_DISCHARGE_CURRENT_ENTITY}:": "45.0",
        f"{HEATING_ENTITY}:": "heat",
        f"{HEATING_ENTITY}:temperature": "22.0",
        f"{PRICE_FORECAST_ENTITY}:": "500.0",
        f"{PV_FORECAST_TODAY_ENTITY}:detailedHourly": pv_forecast_today,
        f"{PV_FORECAST_TOMORROW_ENTITY}:detailedHourly": pv_forecast_tomorrow,
        f"{WEATHER_FORECAST_ENTITY}:forecast": weather_forecast,
        f"{PRICE_FORECAST_ENTITY}:prices": price_forecast,
    }


def test_create(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    state_values: dict,
    pv_forecast_today: list[dict],
    pv_forecast_tomorrow: list[dict],
    weather_forecast: list[dict],
    price_forecast: list[dict],
) -> None:
    mock_appdaemon_state.get_state.side_effect = lambda entity_id, attribute="", *_args, **_kwargs: state_values.get(
        f"{entity_id}:{attribute}"
    )

    result = DefaultSolarStateFactory(mock_appdaemon_logger, mock_appdaemon_state).create()

    assert result is not None
    assert result.battery_soc == BatterySoc(75.5)
    assert result.battery_reserve_soc == BatterySoc(20.0)
    assert result.battery_max_charge_current == BatteryCurrent(50.0)
    assert result.battery_max_discharge_current == BatteryCurrent(50.0)
    assert result.indoor_temperature == Celsius(21.5)
    assert result.outdoor_temperature == Celsius(10.0)
    assert result.is_away_mode is False
    assert result.is_eco_mode is True
    assert result.inverter_storage_mode == StorageMode.SELF_USE
    assert result.is_slot1_discharge_enabled is True
    assert result.slot1_discharge_time == "19:00-20:00"
    assert result.slot1_discharge_current == BatteryCurrent(45.0)
    assert result.hvac_heating_mode == "heat"
    assert result.hvac_heating_temperature == Celsius(22.0)
    assert result.hourly_price == EnergyPrice.pln_per_mwh(Decimal(500))
    assert result.pv_forecast_today == pv_forecast_today
    assert result.pv_forecast_tomorrow == pv_forecast_tomorrow
    assert result.weather_forecast == weather_forecast
    assert result.price_forecast == price_forecast


@pytest.mark.parametrize(
    ("missing_entity", "expected_message"),
    [
        (f"{BATTERY_SOC_ENTITY}:", "Can't create state, missing: battery_soc"),
        (f"{BATTERY_RESERVE_SOC_ENTITY}:", "Can't create state, missing: battery_reserve_soc"),
        (f"{BATTERY_MAX_CHARGE_CURRENT_ENTITY}:", "Can't create state, missing: battery_max_charge_current"),
        (f"{BATTERY_MAX_DISCHARGE_CURRENT_ENTITY}:", "Can't create state, missing: battery_max_discharge_current"),
        (f"{OUTDOOR_TEMPERATURE_ENTITY}:", "Can't create state, missing: outdoor_temperature"),
        (f"{AWAY_MODE_ENTITY}:", "Can't create state, missing: is_away_mode"),
        (f"{ECO_MODE_ENTITY}:", "Can't create state, missing: is_eco_mode"),
        (f"{INVERTER_STORAGE_MODE_ENTITY}:", "Can't create state, missing: inverter_storage_mode"),
        (f"{SLOT1_DISCHARGE_ENABLED_ENTITY}:", "Can't create state, missing: is_slot1_discharge_enabled"),
        (f"{SLOT1_DISCHARGE_TIME_ENTITY}:", "Can't create state, missing: slot1_discharge_time"),
        (f"{SLOT1_DISCHARGE_CURRENT_ENTITY}:", "Can't create state, missing: slot1_discharge_current"),
        (f"{HEATING_ENTITY}:", "Can't create state, missing: hvac_heating_mode"),
        (f"{HEATING_ENTITY}:temperature", "Can't create state, missing: hvac_heating_temperature"),
        (f"{PRICE_FORECAST_ENTITY}:", "Can't create state, missing: hourly_price"),
        (f"{PV_FORECAST_TODAY_ENTITY}:detailedHourly", "Can't create state, missing: pv_forecast_today"),
        (f"{PV_FORECAST_TOMORROW_ENTITY}:detailedHourly", "Can't create state, missing: pv_forecast_tomorrow"),
    ],
)
def test_create_missing_mandatory_field(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    state_values: dict,
    missing_entity: str,
    expected_message: str,
) -> None:
    mock_appdaemon_state.get_state.side_effect = lambda entity_id, attribute="", *_args, **_kwargs: (
        state_values.get(f"{entity_id}:{attribute}") if f"{entity_id}:{attribute}" != missing_entity else None
    )

    result = DefaultSolarStateFactory(mock_appdaemon_logger, mock_appdaemon_state).create()

    assert result is None
    mock_appdaemon_logger.log.assert_called_once_with(expected_message, level=logging.WARNING)


@pytest.mark.parametrize(
    ("missing_entity", "expected_message"),
    [
        (f"{WEATHER_FORECAST_ENTITY}:forecast", "Fallback mode, missing: weather_forecast"),
        (f"{PRICE_FORECAST_ENTITY}:prices", "Fallback mode, missing: price_forecast"),
    ],
)
def test_create_missing_optional_field(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    state_values: dict,
    missing_entity: str,
    expected_message: str,
) -> None:
    mock_appdaemon_state.get_state.side_effect = lambda entity_id, attribute="", *_args, **_kwargs: (
        state_values.get(f"{entity_id}:{attribute}") if f"{entity_id}:{attribute}" != missing_entity else None
    )

    result = DefaultSolarStateFactory(mock_appdaemon_logger, mock_appdaemon_state).create()

    assert result is not None
    mock_appdaemon_logger.log.assert_called_once_with(expected_message, level=logging.WARNING)
