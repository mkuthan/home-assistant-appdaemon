from dataclasses import dataclass

from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh
from units.hourly_period import HourlyPeriod


@dataclass(frozen=True)
class HourlyConsumptionEnergy:
    period: HourlyPeriod
    energy: EnergyKwh


@dataclass(frozen=True)
class HourlyProductionEnergy:
    period: HourlyPeriod
    energy: EnergyKwh


@dataclass(frozen=True)
class HourlyNetEnergy:
    period: HourlyPeriod
    energy: EnergyKwh


class HourlyEnergyAggregator:
    @staticmethod
    def aggregate_hourly_consumption(
        consumptions: list[HourlyConsumptionEnergy],
    ) -> list[HourlyConsumptionEnergy]:
        consumption_dict: dict[HourlyPeriod, EnergyKwh] = {}

        for consumption in consumptions:
            if consumption.period in consumption_dict:
                consumption_dict[consumption.period] += consumption.energy
            else:
                consumption_dict[consumption.period] = consumption.energy

        return [HourlyConsumptionEnergy(period=period, energy=energy) for period, energy in consumption_dict.items()]

    @staticmethod
    def aggregate_hourly_production(
        productions: list[HourlyProductionEnergy],
    ) -> list[HourlyProductionEnergy]:
        production_dict: dict[HourlyPeriod, EnergyKwh] = {}

        for production in productions:
            if production.period in production_dict:
                production_dict[production.period] += production.energy
            else:
                production_dict[production.period] = production.energy

        return [HourlyProductionEnergy(period=period, energy=energy) for period, energy in production_dict.items()]

    @staticmethod
    def aggregate_hourly_net(
        consumptions: list[HourlyConsumptionEnergy],
        productions: list[HourlyProductionEnergy],
    ) -> list[HourlyNetEnergy]:
        net_energy_dict: dict[HourlyPeriod, EnergyKwh] = {}

        for production in productions:
            if production.period in net_energy_dict:
                net_energy_dict[production.period] += production.energy
            else:
                net_energy_dict[production.period] = production.energy

        for consumption in consumptions:
            if consumption.period in net_energy_dict:
                net_energy_dict[consumption.period] -= consumption.energy
            else:
                net_energy_dict[consumption.period] = -consumption.energy

        return [HourlyNetEnergy(period=period, energy=energy) for period, energy in net_energy_dict.items()]

    @staticmethod
    def maximum_cumulative_deficit(nets: list[HourlyNetEnergy]) -> EnergyKwh:
        cumulative_balance = ENERGY_KWH_ZERO
        min_cumulative_balance = ENERGY_KWH_ZERO

        for net in sorted(nets, key=lambda eb: eb.period.start):
            cumulative_balance = cumulative_balance + net.energy

            if cumulative_balance < min_cumulative_balance:
                min_cumulative_balance = cumulative_balance

        return -min_cumulative_balance
