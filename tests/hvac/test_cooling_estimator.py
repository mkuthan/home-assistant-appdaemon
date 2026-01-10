from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

import pytest
from hvac.cooling_estimator import CoolingEstimator
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import Celsius


@pytest.mark.parametrize(
    "now, expected_temp",
    [
        # Just before boost period
        ("2025-10-29T09:59:00+00:00", 24.0),
        # At boost start boundary
        ("2025-10-29T10:00:00+00:00", 22.0),
        # Inside boost period
        ("2025-10-29T14:00:00+00:00", 22.0),
        # At boost end boundary
        ("2025-10-29T18:00:00+00:00", 22.0),
        # Just after boost period
        ("2025-10-29T18:01:00+00:00", 24.0),
    ],
)
def test_estimate_temperature_normal_mode(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
    now: str,
    expected_temp: float,
) -> None:
    configuration = replace(
        configuration,
        cooling_temp_eco_off=Celsius(24.0),
        cooling_boost_time_start_eco_off=time.fromisoformat("10:00:00"),
        cooling_boost_time_end_eco_off=time.fromisoformat("18:00:00"),
    )
    cooling_estimator = CoolingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="cool", is_eco_mode=False)

    result = cooling_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == Celsius(expected_temp)


@pytest.mark.parametrize(
    "now, expected_temp",
    [
        # Just before boost period
        ("2025-10-29T11:59:00+00:00", 26.0),
        # At boost start boundary
        ("2025-10-29T12:00:00+00:00", 24.0),
        # Inside boost period
        ("2025-10-29T13:00:00+00:00", 24.0),
        # At boost end boundary
        ("2025-10-29T16:00:00+00:00", 24.0),
        # Just after boost period
        ("2025-10-29T16:01:00+00:00", 26.0),
    ],
)
def test_estimate_temperature_eco_mode(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
    now: str,
    expected_temp: float,
) -> None:
    configuration = replace(
        configuration,
        cooling_temp_eco_on=Celsius(26.0),
        cooling_boost_time_start_eco_on=time.fromisoformat("12:00:00"),
        cooling_boost_time_end_eco_on=time.fromisoformat("16:00:00"),
    )
    cooling_estimator = CoolingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="cool", is_eco_mode=True)

    result = cooling_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == Celsius(expected_temp)


def test_estimate_temperature_adjustment(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    configuration = replace(
        configuration,
        cooling_temp_eco_off=Celsius(24.0),
        cooling_boost_time_start_eco_off=time.fromisoformat("10:00:00"),
        cooling_boost_time_end_eco_off=time.fromisoformat("18:00:00"),
    )
    cooling_estimator = CoolingEstimator(mock_appdaemon_logger, configuration)

    state = replace(
        state,
        heating_mode="cool",
        is_eco_mode=False,
        cooling_target_temperature=Celsius(24.0),
        temperature_adjustment=Celsius(-1.0),
    )

    outside_boost_datetime = datetime.fromisoformat("2025-10-29T08:00:00+00:00")
    result = cooling_estimator.estimate_temperature(state, outside_boost_datetime)

    assert result == Celsius(23.0)


def test_estimate_temperature_no_change(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    configuration = replace(
        configuration,
        cooling_temp_eco_off=Celsius(24.0),
        cooling_boost_time_start_eco_off=time.fromisoformat("10:00:00"),
        cooling_boost_time_end_eco_off=time.fromisoformat("18:00:00"),
    )
    cooling_estimator = CoolingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="cool", is_eco_mode=False, cooling_target_temperature=Celsius(24.0))

    outside_boost_datetime = datetime.fromisoformat("2025-10-29T08:00:00+00:00")
    result = cooling_estimator.estimate_temperature(state, outside_boost_datetime)

    assert result is None


def test_estimate_temperature_heating_mode_off(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    cooling_estimator = CoolingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="off")

    any_datetime = datetime.fromisoformat("2025-10-29T04:00:00+00:00")
    result = cooling_estimator.estimate_temperature(state, any_datetime)

    assert result is None
