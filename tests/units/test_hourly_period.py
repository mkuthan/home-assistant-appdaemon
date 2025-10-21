from datetime import UTC, datetime

import pytest
from units.hourly_period import HourlyPeriod


def test_valid_hourly_period() -> None:
    start = datetime.fromisoformat("2025-10-21T14:00:00+00:00")
    period = HourlyPeriod(start=start)
    assert period.start == start


def test_naive_datetime_raises_error() -> None:
    naive_datetime = datetime.fromisoformat("2025-10-21T14:00:00")
    with pytest.raises(ValueError, match="Hourly period start must be timezone-aware"):
        HourlyPeriod(start=naive_datetime)


@pytest.mark.parametrize(
    ("minute", "second", "microsecond"),
    [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ],
)
def test_non_hour_start_raises_error(minute: int, second: int, microsecond: int) -> None:
    invalid_start = datetime(2025, 10, 21, 14, minute, second, microsecond, tzinfo=UTC)
    with pytest.raises(ValueError, match="Hourly period start must be at the beginning of an hour"):
        HourlyPeriod(start=invalid_start)


def test_string_representation() -> None:
    start = "2025-10-21T14:00:00+00:00"
    period = HourlyPeriod(start=datetime.fromisoformat(start))
    assert str(period) == start
