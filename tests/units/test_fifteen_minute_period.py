from datetime import UTC, datetime, time

import pytest
from units.fifteen_minute_period import FifteenMinutePeriod


def test_valid_fifteen_minute_period() -> None:
    start = datetime.fromisoformat("2025-10-21T14:00:00+00:00")
    period = FifteenMinutePeriod(start=start)
    assert period.start == start


def test_naive_datetime_raises_error() -> None:
    start = datetime.fromisoformat("2025-10-21T14:00:00")
    with pytest.raises(ValueError, match="Fifteen minute period start must be timezone-aware"):
        FifteenMinutePeriod(start=start)


@pytest.mark.parametrize(
    ("minute", "second", "microsecond"),
    [
        (1, 0, 0),
        (14, 0, 0),
        (16, 0, 0),
        (29, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ],
)
def test_non_fifteen_minute_start_raises_error(minute: int, second: int, microsecond: int) -> None:
    start = datetime(2025, 10, 21, 14, minute, second, microsecond, tzinfo=UTC)
    with pytest.raises(
        ValueError, match="Fifteen minute period start must be at the beginning of a 15-minute interval"
    ):
        FifteenMinutePeriod(start=start)


@pytest.mark.parametrize(
    "minute",
    [0, 15, 30, 45],
)
def test_valid_fifteen_minute_intervals(minute: int) -> None:
    start = datetime(2025, 10, 21, 14, minute, 0, 0, tzinfo=UTC)
    period = FifteenMinutePeriod(start=start)
    assert period.start == start


def test_str() -> None:
    start = "2025-10-21T14:15:00+00:00"
    period = FifteenMinutePeriod(start=datetime.fromisoformat(start))
    assert f"{period}" == start


def test_start_time_end_time() -> None:
    period = FifteenMinutePeriod.parse("2025-10-03T15:00:00+00:00")

    assert period.start_time() == time(15, 0, 0)
    assert period.end_time() == time(15, 15, 0)


def test_parse() -> None:
    start = "2025-10-21T14:30:00+00:00"
    period = FifteenMinutePeriod.parse(start)
    assert period.start == datetime.fromisoformat(start)
