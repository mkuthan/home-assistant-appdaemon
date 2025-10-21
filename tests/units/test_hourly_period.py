from datetime import UTC, datetime, time

import pytest
from units.hourly_period import HourlyPeriod


def test_valid_hourly_period() -> None:
    start = datetime.fromisoformat("2025-10-21T14:00:00+00:00")
    period = HourlyPeriod(start=start)
    assert period.start == start


def test_naive_datetime_raises_error() -> None:
    start = datetime.fromisoformat("2025-10-21T14:00:00")
    with pytest.raises(ValueError, match="Hourly period start must be timezone-aware"):
        HourlyPeriod(start=start)


@pytest.mark.parametrize(
    ("minute", "second", "microsecond"),
    [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ],
)
def test_non_hour_start_raises_error(minute: int, second: int, microsecond: int) -> None:
    start = datetime(2025, 10, 21, 14, minute, second, microsecond, tzinfo=UTC)
    with pytest.raises(ValueError, match="Hourly period start must be at the beginning of an hour"):
        HourlyPeriod(start=start)


def test_str() -> None:
    start = "2025-10-21T14:00:00+00:00"
    period = HourlyPeriod(start=datetime.fromisoformat(start))
    assert f"{period}" == start


def test_start_time_end_time() -> None:
    period = HourlyPeriod.parse("2025-10-03T15:00:00+00:00")

    assert period.start_time() == time(15, 0, 0)
    assert period.end_time() == time(16, 0, 0)


def test_parse() -> None:
    start = "2025-10-21T14:00:00+00:00"
    period = HourlyPeriod.parse(start)
    assert period.start == datetime.fromisoformat(start)
