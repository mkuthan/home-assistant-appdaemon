from units.energy_price import EnergyPrice


def adjust_export_threshold_price(
    pv_export_threshold_price: EnergyPrice,
    tomorrow_midday_average_price: EnergyPrice,
) -> EnergyPrice:
    price_adjustment = pv_export_threshold_price - tomorrow_midday_average_price.non_negative()
    return price_adjustment.non_negative()
