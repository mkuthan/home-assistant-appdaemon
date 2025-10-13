from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

import pytest
from solar.solar import Solar
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from solar.storage_mode import StorageMode
from units.battery_current import BATTERY_CURRENT_ZERO, BatteryCurrent
from units.battery_discharge_slot import BatteryDischargeSlot
from units.battery_soc import BatterySoc


@pytest.fixture
def mock_state_factory() -> Mock:
    return Mock()


@pytest.fixture
def mock_battery_discharge_slot_estimator() -> Mock:
    return Mock()


@pytest.fixture
def mock_battery_reserve_soc_estimator() -> Mock:
    return Mock()


@pytest.fixture
def mock_storage_mode_estimator() -> Mock:
    return Mock()


@pytest.fixture
def solar(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_service: Mock,
    config: SolarConfiguration,
    mock_state_factory: Mock,
    mock_battery_discharge_slot_estimator: Mock,
    mock_battery_reserve_soc_estimator: Mock,
    mock_storage_mode_estimator: Mock,
) -> Solar:
    return Solar(
        mock_appdaemon_logger,
        mock_appdaemon_service,
        config,
        mock_state_factory,
        mock_battery_discharge_slot_estimator,
        mock_battery_reserve_soc_estimator,
        mock_storage_mode_estimator,
    )


def test_align_battery_reserve_soc(
    solar: Solar,
    state: State,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_reserve_soc_estimator: Mock,
) -> None:
    current_battery_reserve_soc = BatterySoc(30.0)
    new_battery_reserve_soc = BatterySoc(40.0)

    state = replace(state, battery_reserve_soc=current_battery_reserve_soc)

    mock_state_factory.create.return_value = state

    mock_battery_reserve_soc_estimator.return_value = new_battery_reserve_soc

    start_period = datetime.now()
    solar.align_battery_reserve_soc(start_period, period_hours=6)

    mock_battery_reserve_soc_estimator.assert_called_once_with(state, start_period, 6)

    mock_appdaemon_service.call_service.assert_called_once_with(
        "number/set_value",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="number.solis_control_battery_reserve_soc",
        value=new_battery_reserve_soc.value,
    )


def test_reset_battery_reserve_soc(
    solar: Solar,
    state: State,
    config: SolarConfiguration,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
) -> None:
    battery_reserve_soc_current = BatterySoc(50.0)
    battery_reserve_soc_min = BatterySoc(20.0)

    # Modify the config on the solar instance directly
    solar.config = replace(config, battery_reserve_soc_min=battery_reserve_soc_min)
    state = replace(state, battery_reserve_soc=battery_reserve_soc_current)

    mock_state_factory.create.return_value = state

    solar.reset_battery_reserve_soc()

    mock_appdaemon_service.call_service.assert_called_once_with(
        "number/set_value",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="number.solis_control_battery_reserve_soc",
        value=battery_reserve_soc_min.value,
    )


def test_schedule_battery_discharge(
    solar: Solar,
    state: State,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_discharge_slot_estimator: Mock,
) -> None:
    current_slot1_discharge_time = "00:00-00:00"
    current_slot1_discharge_current = BATTERY_CURRENT_ZERO

    new_slot1_discharge_time = "18:00-19:00"
    new_slot1_discharge_current = BatteryCurrent(30.0)

    state = replace(
        state,
        is_slot1_discharge_enabled=False,
        slot1_discharge_time=current_slot1_discharge_time,
        slot1_discharge_current=current_slot1_discharge_current,
    )
    mock_state_factory.create.return_value = state

    estimated_discharge_slot = BatteryDischargeSlot(
        start_time=time(18, 0),
        end_time=time(19, 0),
        current=new_slot1_discharge_current,
    )
    mock_battery_discharge_slot_estimator.return_value = estimated_discharge_slot

    start_period = datetime.now()
    solar.schedule_battery_discharge(start_period, period_hours=6)

    mock_battery_discharge_slot_estimator.assert_called_once_with(state, start_period, 6)

    assert mock_appdaemon_service.call_service.call_count == 3
    mock_appdaemon_service.call_service.assert_any_call(
        "text/set_value",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="text.solis_control_slot1_discharge_time",
        value=new_slot1_discharge_time,
    )
    mock_appdaemon_service.call_service.assert_any_call(
        "number/set_value",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="number.solis_control_slot1_discharge_current",
        value=new_slot1_discharge_current.value,
    )
    mock_appdaemon_service.call_service.assert_any_call(
        "switch/turn_on",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="switch.solis_control_slot1_discharge",
    )


def test_disable_battery_discharge(
    solar: Solar,
    state: State,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
) -> None:
    state = replace(state, is_slot1_discharge_enabled=True)
    mock_state_factory.create.return_value = state

    solar.disable_battery_discharge()

    mock_appdaemon_service.call_service.assert_called_once_with(
        "switch/turn_off",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="switch.solis_control_slot1_discharge",
    )


def test_align_storage_mode(
    solar: Solar,
    state: State,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_storage_mode_estimator: Mock,
) -> None:
    current_storage_mode = StorageMode.SELF_USE
    new_storage_mode = StorageMode.FEED_IN_PRIORITY

    state = replace(state, inverter_storage_mode=current_storage_mode)
    mock_state_factory.create.return_value = state

    mock_storage_mode_estimator.return_value = new_storage_mode

    start_period = datetime.now()
    solar.align_storage_mode(start_period, period_hours=6)

    mock_storage_mode_estimator.assert_called_once_with(state, start_period, 6)

    mock_appdaemon_service.call_service.assert_called_once_with(
        "select/select_option",
        callback=mock_appdaemon_service.service_call_callback,
        entity_id="select.solis_control_storage_mode",
        option=new_storage_mode.value,
    )
