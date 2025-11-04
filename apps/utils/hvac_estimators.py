# Heat pump COP characteristics
from units.celsius import Celsius
from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh

_REFERENCE_TEMPERATURE = Celsius(7.0)  # temperature at which COP is rated
_COP_TEMPERATURE_COEFFICIENT = 0.033  # COP change per degree Celsius
_COP_COEFFICIENT_MIN = 0.5  # minimum COP multiplier to prevent unrealistic values

# Frosting cycle parameters
_FROSTING_TEMP_MIN = Celsius(0.0)  # lower bound for frosting conditions
_FROSTING_TEMP_MAX = Celsius(7.0)  # upper bound for frosting conditions
_FROSTING_TEMP_PEAK = Celsius(3.5)  # temperature with maximum frosting risk
_FROSTING_HUMIDITY_THRESHOLD = 70.0  # % - minimum humidity for frosting
_FROSTING_PENALTY_MAX = 0.15  # maximum COP reduction due to frosting cycles (15%)


def estimate_heating_energy_consumption(
    t_out: Celsius,
    t_in: Celsius,
    humidity: float,
    cop_at_7c: float,
    h: float,
) -> EnergyKwh:
    """Estimate heating energy consumption based on temperature differential and environmental conditions.

    This function estimates the electrical energy consumption of a heat pump by accounting for:
    - Heat loss proportional to indoor/outdoor temperature difference
    - COP (Coefficient of Performance) variation with outdoor temperature
    - COP degradation due to frosting cycles in specific temperature and humidity ranges

    The model assumes linear heat loss and uses empirically-derived adjustments for
    real-world heat pump performance characteristics.

    Args:
        t_out: Outdoor temperature.
        t_in: Indoor temperature.
        humidity: Relative humidity as a percentage (0-100).
        cop_at_7c: Heat pump's rated COP at the reference temperature of 7°C.
        h: Heat transfer coefficient representing building heat loss rate in kW/°C.

    Returns:
        Energy consumption in kW. Returns 0.0 if indoor temperature is less than
        or equal to outdoor temperature (no heating required).
    """
    t_diff = t_in - t_out

    if t_diff.value > 0:
        heat_loss = h * t_diff.value

        temperature_coefficient = _temperature_coefficient(t_out)
        frosting_penalty = _frosting_penalty(t_out, humidity)
        adjusted_cop = cop_at_7c * temperature_coefficient * frosting_penalty

        energy_consumption = EnergyKwh(heat_loss / adjusted_cop)
    else:
        energy_consumption = ENERGY_KWH_ZERO

    return energy_consumption


def _temperature_coefficient(
    t_out: Celsius,
) -> float:
    temp_delta = t_out - _REFERENCE_TEMPERATURE
    coefficient = 1.0 + (temp_delta.value * _COP_TEMPERATURE_COEFFICIENT)

    return max(_COP_COEFFICIENT_MIN, coefficient)


def _frosting_penalty(
    t_out: Celsius,
    humidity: float,
) -> float:
    if not (_FROSTING_TEMP_MIN <= t_out <= _FROSTING_TEMP_MAX and humidity > _FROSTING_HUMIDITY_THRESHOLD):
        return 1.0

    distance_from_peak = abs(t_out.value - _FROSTING_TEMP_PEAK.value)
    frosting_severity = (_FROSTING_TEMP_PEAK.value - distance_from_peak) / _FROSTING_TEMP_PEAK.value

    humidity_factor = (humidity - _FROSTING_HUMIDITY_THRESHOLD) / (100.0 - _FROSTING_HUMIDITY_THRESHOLD)

    penalty = _FROSTING_PENALTY_MAX * frosting_severity * humidity_factor

    return 1.0 - penalty
