from datetime import datetime, timedelta


def find_max_revenue_period(
    hourly_periods: list[tuple[datetime, float]], max_duration_minutes: int, min_price_threshold: float
) -> tuple[float, datetime, datetime] | None:
    """
    Find the continuous time period with the largest revenue.

    This algorithm evaluates all possible starting minutes (not just hour boundaries)
    to find the optimal window with maximum revenue. This ensures we don't miss
    optimal solutions that start mid-hour.

    Args:
        hourly_periods: Sorted list of (timestamp, hourly_price) tuples with no gaps.
                       Each tuple represents a 1-hour period starting at timestamp.
                       The price is the hourly rate ($/hour).
        max_duration_minutes: Maximum allowed duration for the period in minutes.
                             Can be any value (e.g., 28, 105, 180).
        min_price_threshold: Minimum hourly price threshold ($/hour) that must
                            apply to each individual period in the window.

    Returns:
        Tuple of (revenue, start_time, end_time) if a valid period exists,
        None otherwise.

    Constraints:
        - Returned period must be a continuous interval between 1 minute
          and max_duration_minutes.
        - Returns None if no period fulfills the price threshold requirement.
        - Price threshold applies to each period's hourly rate, not average price.

    Time Complexity: O(n * m) where n is number of periods and m is minutes per period
    Space Complexity: O(1) auxiliary space
    """
    if not hourly_periods or max_duration_minutes < 1:
        return None

    PERIOD_DURATION_MINUTES = 60
    n = len(hourly_periods)

    # Check if any periods meet the threshold
    if not any(hourly_price >= min_price_threshold for _, hourly_price in hourly_periods):
        return None

    max_revenue = None
    best_start_time = None
    best_end_time = None

    # Try all possible starting positions (including mid-hour starts)
    for start_period_idx in range(n):
        start_period_timestamp, start_period_price = hourly_periods[start_period_idx]

        # Skip if starting period doesn't meet threshold
        if start_period_price < min_price_threshold:
            continue

        # Try starting at each minute within this period
        for start_offset_minutes in range(PERIOD_DURATION_MINUTES):
            start_time = start_period_timestamp + timedelta(minutes=start_offset_minutes)

            # Calculate revenue for a window of max_duration_minutes from this start
            revenue = 0.0
            minutes_covered = 0

            # Iterate through periods that this window spans
            current_period_idx = start_period_idx
            minutes_into_current_period = start_offset_minutes

            while minutes_covered < max_duration_minutes and current_period_idx < n:
                period_timestamp, period_price = hourly_periods[current_period_idx]

                # Check threshold - stop if this period doesn't meet it
                if period_price < min_price_threshold:
                    break

                # Calculate how many minutes to take from this period
                minutes_available_in_period = PERIOD_DURATION_MINUTES - minutes_into_current_period
                minutes_needed = max_duration_minutes - minutes_covered
                minutes_to_take = min(minutes_available_in_period, minutes_needed)

                # Add revenue
                price_per_minute = period_price / PERIOD_DURATION_MINUTES
                revenue += price_per_minute * minutes_to_take
                minutes_covered += minutes_to_take

                # Move to next period
                current_period_idx += 1
                minutes_into_current_period = 0

            # Check if this is a valid and better solution
            if minutes_covered >= 1:
                end_time = start_time + timedelta(minutes=minutes_covered)

                if max_revenue is None or revenue > max_revenue:
                    max_revenue = revenue
                    best_start_time = start_time
                    best_end_time = end_time

    if max_revenue is not None:
        return (max_revenue, best_start_time, best_end_time)

    return None
