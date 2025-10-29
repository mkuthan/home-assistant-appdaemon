from datetime import time


def is_time_in_range(current_time: time, start_time: time, end_time: time) -> bool:
    """Check if current time falls within a time range, handling ranges that cross midnight.

    Args:
        current_time: The time to check.
        start_time: The start of the time range.
        end_time: The end of the time range.

    Returns:
        True if current_time is within the range [start_time, end_time], False otherwise.
        Handles time ranges that cross midnight (e.g., 22:00 to 06:00).
    """
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        return current_time >= start_time or current_time <= end_time
