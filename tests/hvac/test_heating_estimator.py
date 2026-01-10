from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

import pytest
from hvac.heating_estimator import HeatingEstimator
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import Celsius


@pytest.mark.parametrize(
    "now, expected_temp",
    [
        # Just before boost period
        ("2025-10-29T04:59:00+00:00", 21.0),
        # At boost start boundary
        ("2025-10-29T05:00:00+00:00", 22.0),
        # Inside boost period
        ("2025-10-29T12:00:00+00:00", 22.0),
        # At boost end boundary
        ("2025-10-29T21:00:00+00:00", 22.0),
        # Just after boost period
        ("2025-10-29T21:01:00+00:00", 21.0),
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
        heating_temp_eco_off=Celsius(21.0),
        heating_boost_time_start_eco_off=time.fromisoformat("05:00:00"),
        heating_boost_time_end_eco_off=time.fromisoformat("21:00:00"),
    )
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="heat", is_eco_mode=False)

    result = heating_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == Celsius(expected_temp)


@pytest.mark.parametrize(
    "now, expected_temp",
    [
        # Just before boost period
        ("2025-10-29T22:04:00+00:00", 18.0),
        # At boost start boundary
        ("2025-10-29T22:05:00+00:00", 19.0),
        # Inside boost period
        ("2025-10-23T02:00:00+00:00", 19.0),
        # At boost end boundary
        ("2025-10-30T06:55:00+00:00", 19.0),
        # Just after boost period
        ("2025-10-30T06:56:00+00:00", 18.0),
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
        heating_temp_eco_on=Celsius(18.0),
        heating_boost_time_start_eco_on=time.fromisoformat("22:05:00"),
        heating_boost_time_end_eco_on=time.fromisoformat("06:55:00"),
    )
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="heat", is_eco_mode=True)

    result = heating_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == Celsius(expected_temp)


def test_estimate_temperature_adjustment(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    configuration = replace(
        configuration,
        heating_temp_eco_off=Celsius(21.0),
        heating_boost_time_start_eco_off=time.fromisoformat("05:00:00"),
        heating_boost_time_end_eco_off=time.fromisoformat("21:00:00"),
    )
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(
        state,
        heating_mode="heat",
        is_eco_mode=False,
        heating_target_temperature=Celsius(21.0),
        temperature_adjustment=Celsius(1.0),
    )

    outside_boost_datetime = datetime.fromisoformat("2025-10-29T04:00:00+00:00")
    result = heating_estimator.estimate_temperature(state, outside_boost_datetime)

    assert result == Celsius(22.0)


def test_estimate_temperature_no_change(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    configuration = replace(
        configuration,
        heating_temp_eco_off=Celsius(21.0),
        heating_boost_time_start_eco_off=time.fromisoformat("05:00:00"),
        heating_boost_time_end_eco_off=time.fromisoformat("21:00:00"),
    )
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="heat", is_eco_mode=False, heating_target_temperature=Celsius(21.0))

    outside_boost_datetime = datetime.fromisoformat("2025-10-29T04:00:00+00:00")
    result = heating_estimator.estimate_temperature(state, outside_boost_datetime)

    assert result is None


def test_estimate_temperature_heating_mode_off(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="off")

    any_datetime = datetime.fromisoformat("2025-10-29T04:00:00+00:00")
    result = heating_estimator.estimate_temperature(state, any_datetime)

    assert result is None
