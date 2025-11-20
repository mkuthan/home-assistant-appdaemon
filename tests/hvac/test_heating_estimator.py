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
        # Outside boost period
        ("2025-10-29T04:00:00+00:00", Celsius(21.0)),
        # Inside boost period
        ("2025-10-29T10:00:00+00:00", Celsius(22.0)),
        # At boost start boundary
        ("2025-10-29T05:00:00+00:00", Celsius(22.0)),
        # At boost end boundary
        ("2025-10-29T21:00:00+00:00", Celsius(22.0)),
    ],
)
def test_estimate_temperature_normal_mode(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
    now: str,
    expected_temp: Celsius,
) -> None:
    configuration = replace(
        configuration,
        heating_temp=Celsius(21.0),
        heating_boost_delta_temp=Celsius(1.0),
        heating_boost_time_start_eco_off=time.fromisoformat("05:00:00"),
        heating_boost_time_end_eco_off=time.fromisoformat("21:00:00"),
    )
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="heat", is_eco_mode=False)

    result = heating_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == expected_temp


@pytest.mark.parametrize(
    "now, expected_temp",
    [
        # Outside boost period
        ("2025-10-29T08:00:00+00:00", Celsius(18.0)),
        # Inside boost period
        ("2025-10-29T23:00:00+00:00", Celsius(20.0)),
        # At boost start boundary
        ("2025-10-29T22:05:00+00:00", Celsius(20.0)),
        # At boost end boundary
        ("2025-10-29T06:55:00+00:00", Celsius(20.0)),
    ],
)
def test_estimate_temperature_eco_mode(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
    now: str,
    expected_temp: Celsius,
) -> None:
    configuration = replace(
        configuration,
        heating_temp_eco=Celsius(18.0),
        heating_boost_delta_temp_eco=Celsius(2.0),
        heating_boost_time_start_eco_on=time.fromisoformat("22:05:00"),
        heating_boost_time_end_eco_on=time.fromisoformat("06:55:00"),
    )
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="heat", is_eco_mode=True)

    result = heating_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == expected_temp


def test_estimate_temperature_adjustment(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    configuration = replace(
        configuration,
        heating_temp=Celsius(21.0),
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

    result = heating_estimator.estimate_temperature(state, datetime.fromisoformat("2025-10-29T04:00:00+00:00"))

    assert result == Celsius(22.0)


def test_estimate_temperature_no_change(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    configuration = replace(
        configuration,
        heating_temp=Celsius(21.0),
        heating_boost_time_start_eco_off=time.fromisoformat("05:00:00"),
        heating_boost_time_end_eco_off=time.fromisoformat("21:00:00"),
    )
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="heat", is_eco_mode=False, heating_target_temperature=Celsius(21.0))

    result = heating_estimator.estimate_temperature(state, datetime.fromisoformat("2025-10-29T04:00:00+00:00"))

    assert result is None


def test_estimate_temperature_heating_mode_off(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    heating_estimator = HeatingEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, heating_mode="off")

    result = heating_estimator.estimate_temperature(state, datetime.fromisoformat("2025-10-29T04:00:00+00:00"))

    assert result is None
