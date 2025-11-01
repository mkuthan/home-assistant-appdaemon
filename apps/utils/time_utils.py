from datetime import datetime, time, timedelta


def is_time_in_range(current_time: time, start_time: time, end_time: time) -> bool:
    """Check if current time falls within a time range, handling ranges that cross midnight.

    Args:
        current_time: The time to check.
        start_time: The start of the time range.
        end_time: The end of the time range.

    Returns:
        True if current_time is within the range [start_time, end_time], False otherwise.
    """
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        return current_time >= start_time or current_time <= end_time


def hours_difference(start_time: time, end_time: time) -> int:
    """Calculate the difference in hours between two times, handling ranges that cross midnight.

    Args:
        start_time: The start time.
        end_time: The end time.
    Returns:
        The difference in hours rounded to the nearest whole hour.
    """
    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    if end_datetime < start_datetime:
        end_datetime += timedelta(days=1)

    difference = end_datetime - start_datetime
    difference_hours = difference.total_seconds() / 3600

    return round(difference_hours)


def truncate_to_hour(dt: datetime) -> datetime:
    """Truncate datetime to the hour by setting minutes, seconds, and microseconds to zero.

    Args:
        dt: The datetime to truncate.

    Returns:
        A new datetime with only year, month, day, and hour preserved.
    """
    return dt.replace(minute=0, second=0, microsecond=0)
