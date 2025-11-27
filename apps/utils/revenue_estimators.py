from datetime import datetime, timedelta
from decimal import Decimal

from units.energy_price import EnergyPrice
from units.hourly_price import HourlyPrice


def find_max_revenue_period(
    hourly_prices: list[HourlyPrice], min_price_threshold: EnergyPrice, max_duration_minutes: int
) -> tuple[EnergyPrice, datetime, datetime] | None:
    """
    Find the continuous time period with the largest revenue.

    This algorithm evaluates all possible starting minutes to find the optimal window with maximum revenue.
    This ensures we don't miss optimal solutions that start mid-hour.

    Args:
        hourly_prices: Sorted list of hourly prices with no gaps.
        min_price_threshold: Minimum hourly price threshold that must apply to each individual period in the window.
        max_duration_minutes: Maximum allowed duration for the period in minutes. Can be any value (e.g. 28, 105, 180).

    Returns:
        Tuple of (revenue, start_time, end_time) if a valid period exists,
        None otherwise.

    Time Complexity: O(n * d) where n is number of periods and d is max_duration_minutes
    """
    if max_duration_minutes < 1:
        raise ValueError(f"max_duration_minutes must be at least 1, got {max_duration_minutes}")

    if not hourly_prices:
        return None

    if not any(hourly_price.price >= min_price_threshold for hourly_price in hourly_prices):
        return None

    period_duration_minutes = 60

    max_revenue = None
    best_start_time = None
    best_end_time = None

    # Use variable-length sliding window algorithm, optimized two-pointer sliding window approach is not applicable here
    for start_hour_idx, start_hour in enumerate(hourly_prices):
        # Skip if period doesn't meet price threshold
        if start_hour.price < min_price_threshold:
            continue

        # Try starting at each minute within this period
        for start_offset_minutes in range(period_duration_minutes):
            start_time = start_hour.period.start + timedelta(minutes=start_offset_minutes)

            # Calculate revenue for a window of max_duration_minutes from this start
            revenue = start_hour.price.zeroed()
            minutes_covered = 0

            # Iterate through periods that this window spans
            current_period_idx = start_hour_idx
            minutes_into_current_period = start_offset_minutes

            while minutes_covered < max_duration_minutes and current_period_idx < len(hourly_prices):
                current_hourly_price = hourly_prices[current_period_idx]

                # Check threshold - stop if this period doesn't meet it
                if current_hourly_price.price < min_price_threshold:
                    break

                # Calculate how many minutes to take from this period
                minutes_available_in_period = period_duration_minutes - minutes_into_current_period
                minutes_needed = max_duration_minutes - minutes_covered
                minutes_to_take = min(minutes_available_in_period, minutes_needed)

                # Add revenue
                price_per_minute = current_hourly_price.price / Decimal(period_duration_minutes)
                revenue += price_per_minute * Decimal(minutes_to_take)
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

    if max_revenue is None or best_start_time is None or best_end_time is None:
        return None

    return (max_revenue, best_start_time, best_end_time)
