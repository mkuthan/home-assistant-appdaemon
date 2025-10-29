from datetime import time

import pytest
from utils.time_utils import is_time_in_range


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
