from datetime import timedelta
from math import exp, log

from units.celsius import Celsius
from units.hourly_weather import HourlyWeather


def estimate_temperature_decay_time(
    temp_start: Celsius,
    temp_end: Celsius,
    hourly_weather: list[HourlyWeather],
    decay_rate: float,
) -> timedelta:
    """Estimate time for indoor temperature to decay from start to end temperature.

    Uses Newton's Law of Cooling with varying outdoor temperatures. The calculation
    proceeds hour-by-hour, using the outdoor temperature for each period to compute
    the temperature decay during that hour.

    Args:
        temp_start: Initial indoor temperature in Celsius.
        temp_end: Target indoor temperature in Celsius.
        hourly_weather: List of hourly weather data providing outdoor temperatures.
        decay_rate: Thermal decay rate constant k (hour⁻¹), where k = heat_h / thermal_mass.

    Returns:
        Time duration to reach the target temperature.
        Returns timedelta(0) if target is already reached, moving in wrong direction, or no weather data available.

    Raises:
        ValueError: If decay_rate is not positive.
    """
    if decay_rate <= 0:
        raise ValueError("Decay rate must be positive")

    temp_current = temp_start
    temp_target = temp_end

    total_hours = 0.0

    for weather in hourly_weather:
        temp_outdoor = Celsius(weather.temperature)

        if temp_current <= temp_target:
            break

        if temp_current <= temp_outdoor:
            break

        temp_diff_start = temp_current - temp_outdoor
        temp_after_hour = temp_outdoor + Celsius(temp_diff_start.value * exp(-decay_rate * 1.0))

        if temp_after_hour <= temp_target:
            fraction = log(temp_diff_start / (temp_target - temp_outdoor)) / decay_rate
            total_hours += fraction
            break

        temp_current = temp_after_hour
        total_hours += 1.0

    return timedelta(hours=total_hours)
