from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy


def total_surplus(consumptions: list[HourlyConsumptionEnergy], productions: list[HourlyProductionEnergy]) -> EnergyKwh:
    total_surplus = ENERGY_KWH_ZERO

    for consumption in consumptions:
        total_surplus -= consumption.energy

    for production in productions:
        total_surplus += production.energy

    return max(total_surplus, ENERGY_KWH_ZERO)


def maximum_cumulative_deficit(
    consumptions: list[HourlyConsumptionEnergy], productions: list[HourlyProductionEnergy]
) -> EnergyKwh:
    net_energy_dict = {}

    for consumption in consumptions:
        if consumption.period in net_energy_dict:
            net_energy_dict[consumption.period] -= consumption.energy
        else:
            net_energy_dict[consumption.period] = -consumption.energy

    for production in productions:
        if production.period in net_energy_dict:
            net_energy_dict[production.period] += production.energy
        else:
            net_energy_dict[production.period] = production.energy

    net_energy_list = list(net_energy_dict.items())
    net_energy_list_sorted = sorted(net_energy_list, key=lambda n: n[0].start)

    cumulative_balance = ENERGY_KWH_ZERO
    min_cumulative_balance = ENERGY_KWH_ZERO

    for net_energy in net_energy_list_sorted:
        cumulative_balance = cumulative_balance + net_energy[1]

        if cumulative_balance < min_cumulative_balance:
            min_cumulative_balance = cumulative_balance

    return max(-min_cumulative_balance, ENERGY_KWH_ZERO)
