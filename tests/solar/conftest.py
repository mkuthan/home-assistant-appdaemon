from datetime import time
from decimal import Decimal
from unittest.mock import Mock

import pytest
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.storage_mode import StorageMode
from units.battery_current import BATTERY_CURRENT_ZERO
from units.battery_soc import BATTERY_SOC_MIN
from units.battery_voltage import BATTERY_VOLTAGE_ZERO
from units.celsius import CELSIUS_ZERO, Celsius
from units.energy_kwh import ENERGY_KWH_ZERO
from units.energy_price import EnergyPrice


@pytest.fixture
def mock_production_forecast() -> Mock:
    return Mock()


@pytest.fixture
def mock_consumption_forecast() -> Mock:
    return Mock()


@pytest.fixture
def mock_price_forecast() -> Mock:
    return Mock()


@pytest.fixture
def mock_forecast_factory(
    mock_production_forecast: Mock, mock_consumption_forecast: Mock, mock_price_forecast: Mock
) -> Mock:
    mock_forecast_factory = Mock()
    mock_forecast_factory.create_production_forecast.return_value = mock_production_forecast
    mock_forecast_factory.create_consumption_forecast.return_value = mock_consumption_forecast
    mock_forecast_factory.create_price_forecast.return_value = mock_price_forecast

    return mock_forecast_factory


@pytest.fixture
def configuration() -> SolarConfiguration:
    return SolarConfiguration(
        battery_capacity=ENERGY_KWH_ZERO,
        battery_voltage=BATTERY_VOLTAGE_ZERO,
        battery_maximum_current=BATTERY_CURRENT_ZERO,
        battery_reserve_soc_min=BATTERY_SOC_MIN,
        battery_reserve_soc_margin=BATTERY_SOC_MIN,
        battery_reserve_soc_max=BATTERY_SOC_MIN,
        temp_in=Celsius(-1.0),
        heating_cop_at_7c=-1.0,
        heating_h=-1.0,
        temp_out_fallback=Celsius(-1.0),
        humidity_out_fallback=-1.0,
        regular_consumption_away=ENERGY_KWH_ZERO,
        regular_consumption_day=ENERGY_KWH_ZERO,
        regular_consumption_evening=ENERGY_KWH_ZERO,
        pv_export_min_price_margin=EnergyPrice.eur_per_mwh(Decimal(0)),
        battery_export_threshold_price=EnergyPrice.eur_per_mwh(Decimal(0)),
        battery_export_threshold_energy=ENERGY_KWH_ZERO,
        night_low_tariff_time_start=time.fromisoformat("00:00:00"),
        night_low_tariff_time_end=time.fromisoformat("00:00:00"),
        day_low_tariff_time_start=time.fromisoformat("00:00:00"),
        day_low_tariff_time_end=time.fromisoformat("00:00:00"),
    )


@pytest.fixture
def state() -> SolarState:
    return SolarState(
        battery_soc=BATTERY_SOC_MIN,
        battery_reserve_soc=BATTERY_SOC_MIN,
        indoor_temperature=CELSIUS_ZERO,
        outdoor_temperature=CELSIUS_ZERO,
        is_away_mode=False,
        is_eco_mode=False,
        inverter_storage_mode=StorageMode.SELF_USE,
        is_slot1_discharge_enabled=False,
        slot1_discharge_time="",
        slot1_discharge_current=BATTERY_CURRENT_ZERO,
        is_slot2_discharge_enabled=False,
        slot2_discharge_time="",
        slot2_discharge_current=BATTERY_CURRENT_ZERO,
        hvac_heating_mode="",
        hvac_heating_temperature=CELSIUS_ZERO,
        hourly_price=EnergyPrice.pln_per_mwh(Decimal(0)),
        pv_forecast_today=[],
        pv_forecast_tomorrow=[],
        weather_forecast={},
        price_forecast=[],
    )
