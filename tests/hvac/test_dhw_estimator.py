from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

import pytest
from hvac.dhw_estimator import DhwEstimator
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import Celsius


@pytest.mark.parametrize(
    "is_eco_mode, now, expected_temp",
    [
        # Normal mode, outside boost period
        (False, "2025-10-29T08:00:00+00:00", Celsius(48.0)),
        # Normal mode, inside boost period
        (False, "2025-10-29T14:00:00+00:00", Celsius(56.0)),
        # Normal mode, at boost start boundary
        (False, "2025-10-29T13:05:00+00:00", Celsius(56.0)),
        # Normal mode, at boost end boundary
        (False, "2025-10-29T15:55:00+00:00", Celsius(56.0)),
        # Eco mode, outside boost period
        (True, "2025-10-29T08:00:00+00:00", Celsius(40.0)),
        # Eco mode, inside boost period
        (True, "2025-10-29T14:00:00+00:00", Celsius(44.0)),
    ],
)
def test_estimate_temperature(
    mock_appdaemon_logger: Mock,
    configuration: HvacConfiguration,
    state: HvacState,
    is_eco_mode: bool,
    now: str,
    expected_temp: Celsius,
) -> None:
    configuration = replace(
        configuration,
        dhw_temp=Celsius(48.0),
        dhw_temp_eco=Celsius(40.0),
        dhw_boost_delta_temp=Celsius(8.0),
        dhw_boost_delta_temp_eco=Celsius(4.0),
        dhw_boost_start=time.fromisoformat("13:05:00"),
        dhw_boost_end=time.fromisoformat("15:55:00"),
    )
    dhw_estimator = DhwEstimator(mock_appdaemon_logger, configuration)

    state = replace(state, is_eco_mode=is_eco_mode)

    result = dhw_estimator.estimate_temperature(state, datetime.fromisoformat(now))

    assert result == expected_temp
