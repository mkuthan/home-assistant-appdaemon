from unittest.mock import Mock

import pytest
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from solar.storage_mode import StorageMode
from units.battery_current import BATTERY_CURRENT_ZERO
from units.battery_soc import BATTERY_SOC_MIN
from units.battery_voltage import BATTERY_VOLTAGE_ZERO
from units.energy_kwh import ENERGY_KWH_ZERO
from units.energy_price import EnergyPrice


@pytest.fixture
def mock_appdaemon_logger() -> Mock:
    return Mock()


@pytest.fixture
def mock_appdaemon_state() -> Mock:
    return Mock()


@pytest.fixture
def mock_appdaemon_service() -> Mock:
    return Mock()


@pytest.fixture
def config() -> SolarConfiguration:
    return SolarConfiguration(
        battery_capacity=ENERGY_KWH_ZERO,
        battery_voltage=BATTERY_VOLTAGE_ZERO,
        battery_maximum_current=BATTERY_CURRENT_ZERO,
        battery_reserve_soc_min=BATTERY_SOC_MIN,
        battery_reserve_soc_margin=BATTERY_SOC_MIN,
        heating_cop_at_7c=-1.0,
        heating_h=-1.0,
        temp_out_fallback=-1.0,
        humidity_out_fallback=-1.0,
        evening_start_hour=-1,
        regular_consumption_away=ENERGY_KWH_ZERO,
        regular_consumption_day=ENERGY_KWH_ZERO,
        regular_consumption_evening=ENERGY_KWH_ZERO,
        pv_export_threshold_price=EnergyPrice.pln_per_mwh(0.0),
        battery_export_threshold_price=EnergyPrice.pln_per_mwh(0.0),
        battery_export_threshold_energy=ENERGY_KWH_ZERO,
    )


@pytest.fixture
def state() -> State:
    return State(
        battery_soc=BATTERY_SOC_MIN,
        battery_reserve_soc=BATTERY_SOC_MIN,
        indoor_temperature=-1.0,
        outdoor_temperature=-1.0,
        is_away_mode=False,
        is_eco_mode=False,
        inverter_storage_mode=StorageMode.SELF_USE,
        is_slot1_discharge_enabled=False,
        slot1_discharge_time="",
        slot1_discharge_current=BATTERY_CURRENT_ZERO,
        hvac_heating_mode="",
        hourly_price=EnergyPrice.pln_per_mwh(0.0),
        pv_forecast_today=[],
        pv_forecast_tomorrow=[],
        pv_forecast_day_3=[],
        weather_forecast={},
        price_forecast_today=[],
    )
