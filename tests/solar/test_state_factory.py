from decimal import Decimal
from unittest.mock import Mock

import pytest
from entities.entities import ECO_MODE_ENTITY, HEATING_ENTITY
from solar.state_factory import DefaultStateFactory
from solar.storage_mode import StorageMode
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
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
def pv_forecast_day_3() -> list[dict]:
    return [
        {"period_start": "2025-10-07T06:00:00+00:00", "pv_estimate": 0.8},
    ]


@pytest.fixture
def weather_forecast() -> dict:
    return {
        "weather.forecast_wieprz": {
            "forecast": [
                {"datetime": "2025-10-05T14:00:00+00:00", "temperature": 12.0, "humidity": 46.0},
            ]
        }
    }


@pytest.fixture
def price_forecast() -> list[dict]:
    return [
        {"hour": "2025-10-03T16:00:00+00:00", "price": 426.1},
    ]


@pytest.fixture
def state_values(
    pv_forecast_today: list[dict],
    pv_forecast_tomorrow: list[dict],
    pv_forecast_day_3: list[dict],
    price_forecast: list[dict],
) -> dict:
    return {
        "sensor.solis_remaining_battery_capacity:": "75.5",
        "number.solis_control_battery_reserve_soc:": "20.0",
        "sensor.heishamon_z1_actual_temperature:": "21.5",
        "sensor.heishamon_outside_ambient_temperature:": "10.0",
        "input_boolean.away_mode:": "off",
        f"{ECO_MODE_ENTITY}:": "on",
        "select.solis_control_storage_mode:": "Self-Use",
        "switch.solis_control_slot1_discharge:": "on",
        "text.solis_control_slot1_discharge_time:": "19:00-20:00",
        "number.solis_control_slot1_discharge_current:": "45.0",
        "switch.solis_control_slot2_discharge:": "on",
        "text.solis_control_slot2_discharge_time:": "20:00-21:00",
        "number.solis_control_slot2_discharge_current:": "30.0",
        f"{HEATING_ENTITY}:": "heat",
        "sensor.rce:": "500.0",
        "sensor.solcast_pv_forecast_forecast_today:detailedHourly": pv_forecast_today,
        "sensor.solcast_pv_forecast_forecast_tomorrow:detailedHourly": pv_forecast_tomorrow,
        "sensor.solcast_pv_forecast_forecast_day_3:detailedHourly": pv_forecast_day_3,
        "sensor.rce:raw_today": price_forecast,
    }


@pytest.fixture
def service_call_values(
    weather_forecast: dict,
) -> dict:
    return {
        "weather/get_forecasts": weather_forecast,
    }


def test_create(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    mock_appdaemon_service: Mock,
    state_values: dict,
    service_call_values: dict,
    pv_forecast_today: list[dict],
    pv_forecast_tomorrow: list[dict],
    weather_forecast: dict,
    price_forecast: list[dict],
) -> None:
    mock_appdaemon_state.get_state.side_effect = lambda entity_id, attribute="", *_args, **_kwargs: state_values.get(
        f"{entity_id}:{attribute}"
    )
    mock_appdaemon_service.call_service.side_effect = lambda service, *_args, **_kwargs: service_call_values.get(
        service
    )

    result = DefaultStateFactory(mock_appdaemon_logger, mock_appdaemon_state, mock_appdaemon_service).create()

    assert result is not None
    assert result.battery_soc == BatterySoc(75.5)
    assert result.battery_reserve_soc == BatterySoc(20.0)
    assert result.outdoor_temperature == 10.0
    assert result.is_away_mode is False
    assert result.is_eco_mode is True
    assert result.inverter_storage_mode == StorageMode.SELF_USE
    assert result.is_slot1_discharge_enabled is True
    assert result.slot1_discharge_time == "19:00-20:00"
    assert result.slot1_discharge_current == BatteryCurrent(45.0)
    assert result.is_slot2_discharge_enabled is True
    assert result.slot2_discharge_time == "20:00-21:00"
    assert result.slot2_discharge_current == BatteryCurrent(30.0)
    assert result.hvac_heating_mode == "heat"
    assert result.hourly_price == EnergyPrice.pln_per_mwh(Decimal(500))
    assert result.pv_forecast_today == pv_forecast_today
    assert result.pv_forecast_tomorrow == pv_forecast_tomorrow
    assert result.weather_forecast == weather_forecast
    assert result.price_forecast_today == price_forecast


@pytest.mark.parametrize(
    ("missing_entity_or_service", "expected_message"),
    [
        ("sensor.solis_remaining_battery_capacity:", "Missing: battery_soc"),
        ("number.solis_control_battery_reserve_soc:", "Missing: battery_reserve_soc"),
        ("sensor.heishamon_outside_ambient_temperature:", "Missing: outdoor_temperature"),
        ("input_boolean.away_mode:", "Missing: is_away_mode"),
        (f"{ECO_MODE_ENTITY}:", "Missing: is_eco_mode"),
        ("select.solis_control_storage_mode:", "Missing: inverter_storage_mode"),
        ("switch.solis_control_slot1_discharge:", "Missing: is_slot1_discharge_enabled"),
        ("text.solis_control_slot1_discharge_time:", "Missing: slot1_discharge_time"),
        ("number.solis_control_slot1_discharge_current:", "Missing: slot1_discharge_current"),
        ("switch.solis_control_slot2_discharge:", "Missing: is_slot2_discharge_enabled"),
        ("text.solis_control_slot2_discharge_time:", "Missing: slot2_discharge_time"),
        ("number.solis_control_slot2_discharge_current:", "Missing: slot2_discharge_current"),
        (f"{HEATING_ENTITY}:", "Missing: hvac_heating_mode"),
        ("sensor.rce:", "Missing: hourly_price"),
        ("sensor.solcast_pv_forecast_forecast_today:detailedHourly", "Missing: pv_forecast_today"),
        ("sensor.solcast_pv_forecast_forecast_tomorrow:detailedHourly", "Missing: pv_forecast_tomorrow"),
        ("weather/get_forecasts", "Missing: weather_forecast"),
        ("sensor.rce:raw_today", "Missing: price_forecast_today"),
    ],
)
def test_create_missing_field(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    mock_appdaemon_service: Mock,
    state_values: dict,
    service_call_values: dict,
    missing_entity_or_service: str,
    expected_message: str,
) -> None:
    mock_appdaemon_state.get_state.side_effect = (
        lambda entity_id, attribute="", *_args, **_kwargs: state_values.get(f"{entity_id}:{attribute}")
        if f"{entity_id}:{attribute}" != missing_entity_or_service
        else None
    )
    mock_appdaemon_service.call_service.side_effect = (
        lambda service, *_args, **_kwargs: service_call_values.get(service)
        if service != missing_entity_or_service
        else None
    )

    result = DefaultStateFactory(mock_appdaemon_logger, mock_appdaemon_state, mock_appdaemon_service).create()

    assert result is None
    mock_appdaemon_logger.warn.assert_called_once_with(expected_message)
