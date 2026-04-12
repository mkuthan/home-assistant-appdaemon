from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice

_GOOD_DAY_PRODUCTION_FACTOR = 3
_ENERGY_SURPLUS_ADJUSTMENT_FACTOR = 0.5


def adjust_export_threshold_price(
    battery_export_threshold_price: EnergyPrice,
    pv_export_threshold_price: EnergyPrice,
    tomorrow_midday_average_price: EnergyPrice | None,
    tomorrow_production_forecast: EnergyKwh,
    installation_capacity: EnergyKwh,
) -> EnergyPrice:
    is_good_day = tomorrow_production_forecast > installation_capacity * _GOOD_DAY_PRODUCTION_FACTOR
    if is_good_day and tomorrow_midday_average_price is not None:
        price_adjustment = (pv_export_threshold_price - tomorrow_midday_average_price.non_negative()).non_negative()
        return battery_export_threshold_price - price_adjustment
    return battery_export_threshold_price


def adjust_energy_surplus(
    energy_surplus: EnergyKwh,
    nominal_battery_export_threshold_price: EnergyPrice,
    adjusted_battery_export_threshold_price: EnergyPrice,
) -> EnergyKwh:
    if adjusted_battery_export_threshold_price < nominal_battery_export_threshold_price:
        return energy_surplus * _ENERGY_SURPLUS_ADJUSTMENT_FACTOR
    return energy_surplus
