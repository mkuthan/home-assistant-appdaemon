from datetime import datetime
from decimal import Decimal

import pytest
from units.energy_price import EnergyPrice
from units.hourly_period import HourlyPeriod
from units.hourly_price import HourlyPrice
from utils.revenue_estimators import find_max_revenue_period


@pytest.fixture
def any_hourly_periods() -> list[HourlyPrice]:
    return []


@pytest.fixture
def any_energy_price() -> EnergyPrice:
    return EnergyPrice.eur_per_mwh(Decimal(100))


@pytest.fixture
def any_max_duration_minutes() -> int:
    return 60


@pytest.fixture
def standard_periods() -> list[HourlyPrice]:
    return _create_hourly_price_list(
        [
            ("2025-01-01T00:00:00+00:00", 100),
            ("2025-01-01T01:00:00+00:00", 150),
            ("2025-01-01T02:00:00+00:00", 200),
            ("2025-01-01T03:00:00+00:00", 120),
        ]
    )


def test_find_max_revenue_period_28_minutes(standard_periods: list[HourlyPrice]) -> None:
    result = find_max_revenue_period(standard_periods, EnergyPrice.eur_per_mwh(Decimal(100)), 28)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 200 * 28 / 60

    assert revenue.value == pytest.approx(Decimal.from_float(expected_revenue))
    assert start_time == datetime.fromisoformat("2025-01-01T02:00:00+00:00")
    assert end_time == datetime.fromisoformat("2025-01-01T02:28:00+00:00")


def test_find_max_revenue_period_105_minutes(standard_periods: list[HourlyPrice]) -> None:
    result = find_max_revenue_period(standard_periods, EnergyPrice.eur_per_mwh(Decimal(100)), 105)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 150 * 45 / 60 + 200
    assert revenue.value == pytest.approx(Decimal.from_float(expected_revenue))
    assert start_time == datetime.fromisoformat("2025-01-01T01:15:00+00:00")
    assert end_time == datetime.fromisoformat("2025-01-01T03:00:00+00:00")


def test_find_max_revenue_period_105_minutes_high_threshold(standard_periods: list[HourlyPrice]) -> None:
    result = find_max_revenue_period(standard_periods, EnergyPrice.eur_per_mwh(Decimal(160)), 105)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 200.0
    assert revenue.value == pytest.approx(Decimal.from_float(expected_revenue))
    assert start_time == datetime.fromisoformat("2025-01-01T02:00:00+00:00")
    assert end_time == datetime.fromisoformat("2025-01-01T03:00:00+00:00")


def test_find_max_revenue_period_threshold_filtering_in_middle() -> None:
    periods = _create_hourly_price_list(
        [
            ("2025-01-01T00:00:00+00:00", 180),
            ("2025-01-01T01:00:00+00:00", 90),  # Below threshold
            ("2025-01-01T02:00:00+00:00", 200),
            ("2025-01-01T03:00:00+00:00", 170),
        ]
    )

    result = find_max_revenue_period(periods, EnergyPrice.eur_per_mwh(Decimal(150)), 120)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 200.0 + 170.0
    assert revenue.value == pytest.approx(Decimal.from_float(expected_revenue))
    assert start_time == datetime.fromisoformat("2025-01-01T02:00:00+00:00")
    assert end_time == datetime.fromisoformat("2025-01-01T04:00:00+00:00")


def test_find_max_revenue_period_no_periods_meet_threshold(any_max_duration_minutes: int) -> None:
    periods = _create_hourly_price_list(
        [
            ("2025-01-01T00:00:00+00:00", 80),
            ("2025-01-01T01:00:00+00:00", 90),
            ("2025-01-01T02:00:00+00:00", 70),
        ]
    )

    result = find_max_revenue_period(periods, EnergyPrice.eur_per_mwh(Decimal(100)), any_max_duration_minutes)

    assert result is None


def test_find_max_revenue_period_empty_periods(any_energy_price: EnergyPrice, any_max_duration_minutes: int) -> None:
    result = find_max_revenue_period([], any_energy_price, any_max_duration_minutes)

    assert result is None


def test_find_max_revenue_period_zero_duration(
    any_hourly_periods: list[HourlyPrice], any_energy_price: EnergyPrice
) -> None:
    with pytest.raises(ValueError, match="max_duration_minutes must be at least 1"):
        find_max_revenue_period(any_hourly_periods, any_energy_price, 0)


def _create_hourly_price_list(data: list[tuple[str, int]]) -> list[HourlyPrice]:
    return [
        HourlyPrice(
            HourlyPeriod.parse(date_string),
            EnergyPrice.eur_per_mwh(Decimal(price_value)),
        )
        for date_string, price_value in data
    ]
