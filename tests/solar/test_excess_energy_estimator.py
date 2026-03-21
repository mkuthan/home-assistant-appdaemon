from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from solar.excess_energy_estimator import ExcessEnergyEstimator
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_soc import BatterySoc
from units.energy_price import EnergyPrice
from units.money import Money


@pytest.fixture
def excess_energy_estimator(
    configuration: SolarConfiguration,
    mock_appdaemon_logger: Mock,
) -> ExcessEnergyEstimator:
    configuration = replace(
        configuration,
        pv_export_min_price_margin=EnergyPrice.per_mwh(Money.pln(Decimal(200))),
    )
    return ExcessEnergyEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        configuration=configuration,
    )


def test_estimator_turns_on_when_price_low_and_battery_soc_high(
    excess_energy_estimator: ExcessEnergyEstimator,
    state: SolarState,
) -> None:
    state = replace(
        state,
        hourly_price=EnergyPrice.per_mwh(Money.pln(Decimal(150))),
        battery_soc=BatterySoc(95.0),
        is_excess_energy_mode_enabled=False,
    )

    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    is_excess_energy_enabled = excess_energy_estimator.estimate_excess_energy_mode(state, now)

    assert is_excess_energy_enabled is True


def test_estimator_turns_off_when_price_not_low(
    excess_energy_estimator: ExcessEnergyEstimator,
    state: SolarState,
) -> None:
    state = replace(
        state,
        hourly_price=EnergyPrice.per_mwh(Money.pln(Decimal(250))),
        battery_soc=BatterySoc(95.0),
        is_excess_energy_mode_enabled=True,
    )

    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    is_excess_energy_enabled = excess_energy_estimator.estimate_excess_energy_mode(state, now)

    assert is_excess_energy_enabled is False


def test_estimator_turns_off_when_battery_soc_not_high(
    excess_energy_estimator: ExcessEnergyEstimator,
    state: SolarState,
) -> None:
    state = replace(
        state,
        hourly_price=EnergyPrice.per_mwh(Money.pln(Decimal(150))),
        battery_soc=BatterySoc(80.0),
        is_excess_energy_mode_enabled=True,
    )

    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    is_excess_energy_enabled = excess_energy_estimator.estimate_excess_energy_mode(state, now)

    assert is_excess_energy_enabled is False


def test_estimator_returns_none_when_state_unchanged(
    excess_energy_estimator: ExcessEnergyEstimator,
    state: SolarState,
) -> None:
    state = replace(
        state,
        hourly_price=EnergyPrice.per_mwh(Money.pln(Decimal(150))),
        battery_soc=BatterySoc(95.0),
        is_excess_energy_mode_enabled=True,
    )

    now = datetime.fromisoformat("2025-10-10T12:00:00+00:00")

    is_excess_energy_enabled = excess_energy_estimator.estimate_excess_energy_mode(state, now)

    assert is_excess_energy_enabled is None
