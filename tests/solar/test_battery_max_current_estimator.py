from dataclasses import replace
from datetime import datetime
from unittest.mock import Mock

import pytest
from solar.battery_max_current_estimator import BatteryMaxCurrentEstimator
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_current import BatteryCurrent


@pytest.fixture
def battery_max_current_estimator(
    configuration: SolarConfiguration,
    mock_appdaemon_logger: Mock,
) -> BatteryMaxCurrentEstimator:
    configuration = replace(
        configuration,
        battery_maximum_current=BatteryCurrent(80.0),
        battery_nominal_current=BatteryCurrent(50.0),
        battery_night_charge_current=BatteryCurrent(20.0),
    )

    return BatteryMaxCurrentEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        configuration=configuration,
    )


def test_estimate_night_charge_current_at_night(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    now = datetime.fromisoformat("2025-10-10T22:00:00+00:00")

    charge_current = battery_max_current_estimator.estimate_battery_max_charge_current(state, now)

    assert charge_current == BatteryCurrent(20.0)


def test_estimate_nominal_charge_current_during_day(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    charge_current = battery_max_current_estimator.estimate_battery_max_charge_current(state, now)

    assert charge_current == BatteryCurrent(50.0)


def test_estimate_night_charge_current_unchanged(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    state = replace(state, battery_max_charge_current=BatteryCurrent(20.0))
    now = datetime.fromisoformat("2025-10-10T22:00:00+00:00")

    charge_current = battery_max_current_estimator.estimate_battery_max_charge_current(state, now)

    assert charge_current is None


def test_estimate_nominal_charge_current_unchanged(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    state = replace(state, battery_max_charge_current=BatteryCurrent(50.0))
    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    charge_current = battery_max_current_estimator.estimate_battery_max_charge_current(state, now)

    assert charge_current is None


def test_estimate_maximum_discharge_current_inside_slot(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    state = replace(state, is_slot1_discharge_enabled=True, slot1_discharge_time="16:00-21:00")
    now = datetime.fromisoformat("2025-10-10T18:00:00+00:00")

    discharge_current = battery_max_current_estimator.estimate_battery_max_discharge_current(state, now)

    assert discharge_current == BatteryCurrent(80.0)


def test_estimate_nominal_discharge_current_outside_slot(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    state = replace(state, is_slot1_discharge_enabled=True, slot1_discharge_time="16:00-21:00")
    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    discharge_current = battery_max_current_estimator.estimate_battery_max_discharge_current(state, now)

    assert discharge_current == BatteryCurrent(50.0)


def test_estimate_nominal_discharge_current_when_slot_disabled(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    state = replace(state, is_slot1_discharge_enabled=False, slot1_discharge_time="16:00-21:00")
    now = datetime.fromisoformat("2025-10-10T18:00:00+00:00")

    discharge_current = battery_max_current_estimator.estimate_battery_max_discharge_current(state, now)

    assert discharge_current == BatteryCurrent(50.0)


def test_estimate_maximum_discharge_current_unchanged(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    state = replace(
        state,
        is_slot1_discharge_enabled=True,
        slot1_discharge_time="16:00-21:00",
        battery_max_discharge_current=BatteryCurrent(80.0),
    )
    now = datetime.fromisoformat("2025-10-10T18:00:00+00:00")

    discharge_current = battery_max_current_estimator.estimate_battery_max_discharge_current(state, now)

    assert discharge_current is None


def test_estimate_nominal_discharge_current_unchanged(
    battery_max_current_estimator: BatteryMaxCurrentEstimator,
    state: SolarState,
) -> None:
    state = replace(state, battery_max_discharge_current=BatteryCurrent(50.0))
    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    discharge_current = battery_max_current_estimator.estimate_battery_max_discharge_current(state, now)

    assert discharge_current is None
