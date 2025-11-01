from datetime import datetime, time

import pytest
from utils.time_utils import hours_difference, is_time_in_range, truncate_to_hour


@pytest.mark.parametrize(
    "current_time, start_time, end_time, expected",
    [
        # Normal range (doesn't cross midnight)
        ("10:00", "09:00", "17:00", True),
        ("08:00", "09:00", "17:00", False),
        # Range crossing midnight
        ("23:00", "22:00", "06:00", True),
        ("10:00", "22:00", "06:00", False),
    ],
)
def test_is_time_in_range(current_time: str, start_time: str, end_time: str, expected: bool) -> None:
    result = is_time_in_range(
        time.fromisoformat(current_time),
        time.fromisoformat(start_time),
        time.fromisoformat(end_time),
    )
    assert result == expected


@pytest.mark.parametrize(
    "start_time, end_time, expected_hours",
    [
        # Morning high tariff period
        ("06:55:00", "13:05:00", 6),
        ("07:00:00", "13:00:00", 6),
        ("07:05:00", "12:55:00", 6),
        # Evening high tariff period
        ("15:55:00", "22:05:00", 6),
        ("16:00:00", "22:00:00", 6),
        ("16:05:00", "21:55:00", 6),
        # Periods crossing midnight
        ("21:55:00", "02:05:00", 4),
        ("22:00:00", "02:00:00", 4),
        ("22:05:00", "01:55:00", 4),
    ],
)
def test_hours_difference(start_time: str, end_time: str, expected_hours: int) -> None:
    result = hours_difference(
        time.fromisoformat(start_time),
        time.fromisoformat(end_time),
    )
    assert result == expected_hours


@pytest.mark.parametrize(
    "input_datetime, expected_datetime",
    [
        ("2025-11-01T14:30:45.123456", "2025-11-01T14:00:00"),
        ("2025-11-01T00:59:59.999999", "2025-11-01T00:00:00"),
        ("2025-11-01T23:15:30.500000", "2025-11-01T23:00:00"),
        ("2025-11-01T10:00:00", "2025-11-01T10:00:00"),
    ],
)
def test_truncate_to_hour(input_datetime: str, expected_datetime: str) -> None:
    result = truncate_to_hour(datetime.fromisoformat(input_datetime))
    assert result == datetime.fromisoformat(expected_datetime)
