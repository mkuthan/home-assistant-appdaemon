from datetime import datetime

import pytest
from utils.revenue_estimators import find_max_revenue_period


@pytest.fixture
def standard_periods() -> list[tuple[datetime, float]]:
    return [
        (datetime.fromisoformat("2025-01-01T00:00:00"), 100.0),
        (datetime.fromisoformat("2025-01-01T01:00:00"), 150.0),
        (datetime.fromisoformat("2025-01-01T02:00:00"), 200.0),
        (datetime.fromisoformat("2025-01-01T03:00:00"), 120.0),
    ]


def test_find_max_revenue_period_28_minutes(standard_periods: list[tuple[datetime, float]]) -> None:
    result = find_max_revenue_period(standard_periods, 28, 100.0)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 200 * 28 / 60
    assert revenue == pytest.approx(expected_revenue)
    assert start_time == datetime.fromisoformat("2025-01-01T02:00:00")
    assert end_time == datetime.fromisoformat("2025-01-01T02:28:00")


def test_find_max_revenue_period_105_minutes(standard_periods: list[tuple[datetime, float]]) -> None:
    result = find_max_revenue_period(standard_periods, 105, 100.0)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 150 * 45 / 60 + 200
    assert revenue == pytest.approx(expected_revenue)
    assert start_time == datetime.fromisoformat("2025-01-01T01:15:00")
    assert end_time == datetime.fromisoformat("2025-01-01T03:00:00")


def test_find_max_revenue_period_105_minutes_high_threshold(standard_periods: list[tuple[datetime, float]]) -> None:
    result = find_max_revenue_period(standard_periods, 105, 160.0)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 200.0
    assert revenue == pytest.approx(expected_revenue)
    assert start_time == datetime.fromisoformat("2025-01-01T02:00:00")
    assert end_time == datetime.fromisoformat("2025-01-01T03:00:00")

def test_find_max_revenue_period_threshold_filtering_in_middle() -> None:
    periods = [
        (datetime.fromisoformat("2025-01-01T00:00:00"), 180.0),
        (datetime.fromisoformat("2025-01-01T01:00:00"), 90.0),  # Below threshold
        (datetime.fromisoformat("2025-01-01T02:00:00"), 200.0),
        (datetime.fromisoformat("2025-01-01T03:00:00"), 170.0),
    ]

    result = find_max_revenue_period(periods, 120, 150.0)

    assert result is not None
    revenue, start_time, end_time = result

    expected_revenue = 200.0 + 170.0
    assert revenue == pytest.approx(expected_revenue)
    assert start_time == datetime.fromisoformat("2025-01-01T02:00:00")
    assert end_time == datetime.fromisoformat("2025-01-01T04:00:00")


def test_find_max_revenue_period_no_periods_meet_threshold() -> None:
    periods = [
        (datetime.fromisoformat("2025-01-01T00:00:00"), 50.0),
        (datetime.fromisoformat("2025-01-01T01:00:00"), 60.0),
        (datetime.fromisoformat("2025-01-01T02:00:00"), 70.0),
    ]

    result = find_max_revenue_period(periods, 90, 100.0)

    assert result is None


def test_find_max_revenue_period_empty_periods() -> None:
    result = find_max_revenue_period([], 60, 100.0)

    assert result is None


def test_find_max_revenue_period_zero_duration(standard_periods: list[tuple[datetime, float]]) -> None:
    result = find_max_revenue_period(standard_periods, 0, 100.0)

    assert result is None
