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
        heating_temp=CELSIUS_ZERO,
        heating_temp_eco=CELSIUS_ZERO,
        heating_reduced_delta_temp=CELSIUS_ZERO,
        heating_reduced_delta_temp_eco=CELSIUS_ZERO,
        cooling_temp=CELSIUS_ZERO,
        cooling_temp_eco=CELSIUS_ZERO,
        cooling_reduced_delta_temp=CELSIUS_ZERO,
        cooling_reduced_delta_temp_eco=CELSIUS_ZERO,
    )


@pytest.fixture
def state() -> HvacState:
    return HvacState()
