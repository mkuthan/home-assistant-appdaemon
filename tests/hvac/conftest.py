from datetime import time

import pytest
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state import HvacState
from units.celsius import CELSIUS_ZERO


@pytest.fixture
def config() -> HvacConfiguration:
    return HvacConfiguration(
        dhw_temp=CELSIUS_ZERO,
        dhw_temp_eco=CELSIUS_ZERO,
        dhw_boost_delta_temp=CELSIUS_ZERO,
        dhw_boost_delta_temp_eco=CELSIUS_ZERO,
        dhw_boost_start=time.fromisoformat("00:00:00"),
        dhw_boost_end=time.fromisoformat("00:00:00"),
        heating_temp=CELSIUS_ZERO,
        heating_temp_eco=CELSIUS_ZERO,
        heating_boost_delta_temp=CELSIUS_ZERO,
        heating_boost_delta_temp_eco=CELSIUS_ZERO,
        heating_boost_time_start_eco_on=time.fromisoformat("00:00:00"),
        heating_boost_time_end_eco_on=time.fromisoformat("00:00:00"),
        heating_boost_time_start_eco_off=time.fromisoformat("00:00:00"),
        heating_boost_time_end_eco_off=time.fromisoformat("00:00:00"),
        cooling_temp=CELSIUS_ZERO,
        cooling_temp_eco=CELSIUS_ZERO,
        cooling_reduced_delta_temp=CELSIUS_ZERO,
        cooling_reduced_delta_temp_eco=CELSIUS_ZERO,
        cooling_reduced_time_start_eco_on=time.fromisoformat("00:00:00"),
        cooling_reduced_time_end_eco_on=time.fromisoformat("00:00:00"),
        cooling_reduced_time_start_eco_off=time.fromisoformat("00:00:00"),
        cooling_reduced_time_end_eco_off=time.fromisoformat("00:00:00"),
    )


@pytest.fixture
def state() -> HvacState:
    return HvacState()
