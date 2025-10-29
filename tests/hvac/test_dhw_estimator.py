from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

import pytest
from hvac.dhw_estimator import DhwEstimator
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import Celsius


@pytest.mark.parametrize(
    "now, expected_temp",
    [
        # Outside boost period
        ("2025-10-29T08:00:00+00:00", Celsius(48.0)),
        # Inside boost period
        ("2025-10-29T14:00:00+00:00", Celsius(56.0)),
        # At boost start boundary
        ("2025-10-29T13:05:00+00:00", Celsius(56.0)),
        # At boost end boundary
        ("2025-10-29T15:55:00+00:00", Celsius(56.0)),
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
        dhw_temp=Celsius(48.0),
        dhw_boost_delta_temp=Celsius(8.0),
        dhw_boost_start=time.fromisoformat("13:05:00"),
        dhw_boost_end=time.fromisoformat("15:55:00"),
    )
    dhw_estimator = DhwEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, is_eco_mode=False)

    result = dhw_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == expected_temp


@pytest.mark.parametrize(
    "now, expected_temp",
    [
        # Outside boost period
        ("2025-10-29T08:00:00+00:00", Celsius(40.0)),
        # Inside boost period
        ("2025-10-29T14:00:00+00:00", Celsius(44.0)),
        # At boost start boundary
        ("2025-10-29T13:05:00+00:00", Celsius(44.0)),
        # At boost end boundary
        ("2025-10-29T15:55:00+00:00", Celsius(44.0)),
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
        dhw_temp_eco=Celsius(40.0),
        dhw_boost_delta_temp_eco=Celsius(4.0),
        dhw_boost_start=time.fromisoformat("13:05:00"),
        dhw_boost_end=time.fromisoformat("15:55:00"),
    )
    dhw_estimator = DhwEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, is_eco_mode=True)

    result = dhw_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == expected_temp


def test_estimate_temperature_no_change(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
) -> None:
    configuration = replace(
        configuration,
        dhw_temp=Celsius(48.0),
        dhw_boost_start=time.fromisoformat("13:05:00"),
        dhw_boost_end=time.fromisoformat("15:55:00"),
    )
    dhw_estimator = DhwEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, is_eco_mode=False, dhw_temperature=Celsius(48.0))

    result = dhw_estimator.estimate_temperature(state, datetime.fromisoformat("2025-10-29T08:00:00+00:00"))

    assert result is None
