from dataclasses import replace
from datetime import datetime, time
from unittest.mock import ANY, Mock

import pytest
from entities.entities import (
    BATTERY_MAX_CHARGE_CURRENT_ENTITY,
    BATTERY_MAX_DISCHARGE_CURRENT_ENTITY,
    BATTERY_RESERVE_SOC_ENTITY,
    INVERTER_STORAGE_MODE_ENTITY,
    SLOT1_DISCHARGE_CURRENT_ENTITY,
    SLOT1_DISCHARGE_ENABLED_ENTITY,
    SLOT1_DISCHARGE_TIME_ENTITY,
)
from solar.battery_discharge_slot import BatteryDischargeSlot
from solar.solar import Solar
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.storage_mode import StorageMode
from units.battery_current import BATTERY_CURRENT_ZERO, BatteryCurrent
from units.battery_soc import BatterySoc


@pytest.fixture
def mock_state_factory() -> Mock:
    return Mock()


@pytest.fixture
def mock_battery_max_current_estimator() -> Mock:
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
    configuration: SolarConfiguration,
    mock_state_factory: Mock,
    mock_battery_max_current_estimator: Mock,
    mock_battery_discharge_slot_estimator: Mock,
    mock_battery_reserve_soc_estimator: Mock,
    mock_storage_mode_estimator: Mock,
) -> Solar:
    return Solar(
        mock_appdaemon_logger,
        mock_appdaemon_service,
        configuration,
        mock_state_factory,
        mock_battery_max_current_estimator,
        mock_battery_discharge_slot_estimator,
        mock_battery_reserve_soc_estimator,
        mock_storage_mode_estimator,
    )


def test_control_battery_reserve_soc(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_reserve_soc_estimator: Mock,
) -> None:
    current_battery_reserve_soc = BatterySoc(30.0)
    new_battery_reserve_soc = BatterySoc(40.0)

    state = replace(state, battery_reserve_soc=current_battery_reserve_soc)

    mock_state_factory.create.return_value = state

    mock_battery_reserve_soc_estimator.estimate_battery_reserve_soc.return_value = new_battery_reserve_soc

    now = datetime.now()
    solar.control_battery_reserve_soc(now)

    mock_battery_reserve_soc_estimator.estimate_battery_reserve_soc.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_called_once_with(
        "number/set_value",
        callback=ANY,
        entity_id=BATTERY_RESERVE_SOC_ENTITY,
        value=new_battery_reserve_soc.value,
    )


def test_control_battery_reserve_soc_no_change(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_reserve_soc_estimator: Mock,
) -> None:
    current_battery_reserve_soc = BatterySoc(30.0)

    state = replace(state, battery_reserve_soc=current_battery_reserve_soc)

    mock_state_factory.create.return_value = state

    mock_battery_reserve_soc_estimator.estimate_battery_reserve_soc.return_value = None

    now = datetime.now()
    solar.control_battery_reserve_soc(now)

    mock_battery_reserve_soc_estimator.estimate_battery_reserve_soc.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_not_called()


def test_control_battery_max_charge_current(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_max_current_estimator: Mock,
) -> None:
    current_battery_max_charge_current = BatteryCurrent(30.0)
    new_battery_max_charge_current = BatteryCurrent(40.0)

    state = replace(state, battery_max_charge_current=current_battery_max_charge_current)

    mock_state_factory.create.return_value = state

    mock_battery_max_current_estimator.estimate_battery_max_charge_current.return_value = new_battery_max_charge_current

    now = datetime.now()
    solar.control_battery_max_charge_current(now)

    mock_battery_max_current_estimator.estimate_battery_max_charge_current.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_called_once_with(
        "number/set_value",
        callback=ANY,
        entity_id=BATTERY_MAX_CHARGE_CURRENT_ENTITY,
        value=new_battery_max_charge_current.value,
    )


def test_control_battery_max_charge_current_no_change(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_max_current_estimator: Mock,
) -> None:
    current_battery_max_charge_current = BatteryCurrent(30.0)

    state = replace(state, battery_max_charge_current=current_battery_max_charge_current)

    mock_state_factory.create.return_value = state

    mock_battery_max_current_estimator.estimate_battery_max_charge_current.return_value = None

    now = datetime.now()
    solar.control_battery_max_charge_current(now)

    mock_battery_max_current_estimator.estimate_battery_max_charge_current.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_not_called()


def test_control_battery_max_discharge_current(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_max_current_estimator: Mock,
) -> None:
    current_battery_max_discharge_current = BatteryCurrent(30.0)
    new_battery_max_discharge_current = BatteryCurrent(40.0)

    state = replace(state, battery_max_discharge_current=current_battery_max_discharge_current)

    mock_state_factory.create.return_value = state

    mock_battery_max_current_estimator.estimate_battery_max_discharge_current.return_value = (
        new_battery_max_discharge_current
    )

    now = datetime.now()
    solar.control_battery_max_discharge_current(now)

    mock_battery_max_current_estimator.estimate_battery_max_discharge_current.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_called_once_with(
        "number/set_value",
        callback=ANY,
        entity_id=BATTERY_MAX_DISCHARGE_CURRENT_ENTITY,
        value=new_battery_max_discharge_current.value,
    )


def test_control_battery_max_discharge_current_no_change(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_battery_max_current_estimator: Mock,
) -> None:
    current_battery_max_discharge_current = BatteryCurrent(30.0)

    state = replace(state, battery_max_discharge_current=current_battery_max_discharge_current)

    mock_state_factory.create.return_value = state

    mock_battery_max_current_estimator.estimate_battery_max_discharge_current.return_value = None

    now = datetime.now()
    solar.control_battery_max_discharge_current(now)

    mock_battery_max_current_estimator.estimate_battery_max_discharge_current.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_not_called()


def test_control_storage_mode(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_storage_mode_estimator: Mock,
) -> None:
    current_storage_mode = StorageMode.SELF_USE
    new_storage_mode = StorageMode.FEED_IN_PRIORITY

    state = replace(state, inverter_storage_mode=current_storage_mode)
    mock_state_factory.create.return_value = state

    mock_storage_mode_estimator.estimate_storage_mode.return_value = new_storage_mode

    now = datetime.now()
    solar.control_storage_mode(now)

    mock_storage_mode_estimator.estimate_storage_mode.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_called_once_with(
        "select/select_option",
        callback=ANY,
        entity_id=INVERTER_STORAGE_MODE_ENTITY,
        option=new_storage_mode.value,
    )


def test_control_storage_mode_no_change(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
    mock_storage_mode_estimator: Mock,
) -> None:
    current_storage_mode = StorageMode.SELF_USE

    state = replace(state, inverter_storage_mode=current_storage_mode)
    mock_state_factory.create.return_value = state

    mock_storage_mode_estimator.estimate_storage_mode.return_value = None

    now = datetime.now()
    solar.control_storage_mode(now)

    mock_storage_mode_estimator.estimate_storage_mode.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_not_called()


def test_schedule_battery_discharge(
    solar: Solar,
    state: SolarState,
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

    mock_battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm.return_value = estimated_discharge_slot

    now = datetime.now()
    solar.schedule_battery_discharge(now)

    mock_battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm.assert_called_once_with(state, now)

    mock_appdaemon_service.call_service.assert_any_call(
        "text/set_value",
        callback=ANY,
        entity_id=SLOT1_DISCHARGE_TIME_ENTITY,
        value=new_slot1_discharge_time,
    )
    mock_appdaemon_service.call_service.assert_any_call(
        "number/set_value",
        callback=ANY,
        entity_id=SLOT1_DISCHARGE_CURRENT_ENTITY,
        value=new_slot1_discharge_current.value,
    )
    mock_appdaemon_service.call_service.assert_any_call(
        "switch/turn_on",
        callback=ANY,
        entity_id=SLOT1_DISCHARGE_ENABLED_ENTITY,
    )


def test_disable_battery_discharge(
    solar: Solar,
    state: SolarState,
    mock_appdaemon_service: Mock,
    mock_state_factory: Mock,
) -> None:
    state = replace(state, is_slot1_discharge_enabled=True)
    mock_state_factory.create.return_value = state

    solar.disable_battery_discharge()

    mock_appdaemon_service.call_service.assert_any_call(
        "switch/turn_off",
        callback=ANY,
        entity_id=SLOT1_DISCHARGE_ENABLED_ENTITY,
    )
