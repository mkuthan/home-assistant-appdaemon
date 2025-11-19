from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.battery_discharge_slot import BatteryDischargeSlot
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.energy_kwh import EnergyKwh
from utils.battery_estimators import estimate_battery_surplus_energy
from utils.energy_aggregators import maximum_cumulative_deficit
from utils.revenue_estimators import find_max_revenue_period


class BatteryDischargeSlotEstimator:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: SolarConfiguration,
        forecast_factory: ForecastFactory,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration
        self.forecast_factory = forecast_factory

    def estimate_battery_discharge_at_4_pm(self, state: SolarState, now: datetime) -> BatteryDischargeSlot | None:
        today_4_pm = now.replace(hour=16, minute=0, second=0, microsecond=0)
        today_10_pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
        low_tariff_hours = 6

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        hourly_consumptions = consumption_forecast.hourly(today_4_pm, low_tariff_hours)

        production_forecast = self.forecast_factory.create_production_forecast(state)
        hourly_productions = production_forecast.hourly(today_4_pm, low_tariff_hours)

        energy_reserve = maximum_cumulative_deficit(hourly_consumptions, hourly_productions)
        self.appdaemon_logger.log("Energy reserve: %s", energy_reserve)

        energy_surplus = estimate_battery_surplus_energy(
            energy_reserve,
            state.battery_soc,
            self.configuration.battery_capacity,
            self.configuration.battery_reserve_soc_min,
            self.configuration.battery_reserve_soc_margin,
        )
        self.appdaemon_logger.log("Energy surplus: %s", energy_surplus)

        if energy_surplus < self.configuration.battery_export_threshold_energy:
            self.appdaemon_logger.log(
                "Skip, estimated energy surplus %s <= threshold %s",
                energy_surplus,
                self.configuration.battery_export_threshold_energy,
            )
            return None

        battery_discharge_energy_1h = EnergyKwh(
            self.configuration.battery_maximum_current.value * self.configuration.battery_voltage.value / 1000
        )
        hours = energy_surplus / battery_discharge_energy_1h

        price_forecast = self.forecast_factory.create_price_forecast(state)
        hourly_prices = price_forecast.select_hourly_prices(today_4_pm, today_10_pm)

        revenue_period = find_max_revenue_period(
            hourly_prices, self.configuration.battery_export_threshold_price, int(hours * 60)
        )

        match revenue_period:
            case (revenue, start, end):
                discharge_slot = BatteryDischargeSlot(
                    start_time=start.time(),
                    end_time=end.time(),
                    current=self.configuration.battery_maximum_current,
                )
                self.appdaemon_logger.log("Revenue: %s, battery discharge slot: %s", revenue, discharge_slot)

                return discharge_slot
            case None:
                self.appdaemon_logger.log(
                    "Skip, no suitable revenue period found, threshold price: %s",
                    self.configuration.battery_export_threshold_price,
                )
                return None
