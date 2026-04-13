import logging
from datetime import datetime, timedelta

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.battery_discharge_slot import BatteryDischargeSlot
from solar.forecast_factory import ForecastFactory
from solar.price_forecast import PriceForecast
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy
from utils.battery_estimators import estimate_battery_replenish_energy, estimate_battery_surplus_energy
from utils.energy_aggregators import maximum_cumulative_deficit, total_surplus
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
        high_tariff_hours = 6

        tomorrow_7_am = (now + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        daytime_hours = 9

        tomorrow_10_30_am = (now + timedelta(days=1)).replace(hour=10, minute=30, second=0, microsecond=0)
        midday_hours = 4

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)
        price_forecast = self.forecast_factory.create_price_forecast(state)

        hourly_consumptions = consumption_forecast.hourly(today_4_pm, high_tariff_hours)
        hourly_productions = production_forecast.hourly(today_4_pm, high_tariff_hours)
        daytime_consumptions = consumption_forecast.hourly(tomorrow_7_am, daytime_hours)
        daytime_productions = production_forecast.hourly(tomorrow_7_am, daytime_hours)
        midday_average_price = price_forecast.average_price(tomorrow_10_30_am, midday_hours)

        return self._estimate_battery_discharge_slot(
            state,
            self.configuration.battery_discharge_evening_margin,
            hourly_consumptions,
            hourly_productions,
            daytime_consumptions,
            daytime_productions,
            midday_average_price,
            price_forecast,
            today_4_pm,
            today_10_pm,
        )

    def estimate_battery_discharge_at_7_am(self, state: SolarState, now: datetime) -> BatteryDischargeSlot | None:
        today_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0)
        today_9_am = now.replace(hour=9, minute=0, second=0, microsecond=0)
        high_tariff_hours = 6

        daytime_hours = 9

        today_10_30_am = now.replace(hour=10, minute=30, second=0, microsecond=0)
        midday_hours = 4

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)
        price_forecast = self.forecast_factory.create_price_forecast(state)

        hourly_consumptions = consumption_forecast.hourly(today_7_am, high_tariff_hours)
        hourly_productions = production_forecast.hourly(today_7_am, high_tariff_hours)
        daytime_consumptions = consumption_forecast.hourly(today_7_am, daytime_hours)
        daytime_productions = production_forecast.hourly(today_7_am, daytime_hours)
        midday_average_price = price_forecast.average_price(today_10_30_am, midday_hours)

        return self._estimate_battery_discharge_slot(
            state,
            self.configuration.battery_discharge_morning_margin,
            hourly_consumptions,
            hourly_productions,
            daytime_consumptions,
            daytime_productions,
            midday_average_price,
            price_forecast,
            today_7_am,
            today_9_am,
        )

    def _estimate_battery_discharge_slot(
        self,
        state: SolarState,
        margin: EnergyPrice,
        hourly_consumptions: list[HourlyConsumptionEnergy],
        hourly_productions: list[HourlyProductionEnergy],
        daytime_consumptions: list[HourlyConsumptionEnergy],
        daytime_productions: list[HourlyProductionEnergy],
        midday_average_price: EnergyPrice | None,
        price_forecast: PriceForecast,
        discharge_window_start: datetime,
        discharge_window_end: datetime,
    ) -> BatteryDischargeSlot | None:
        discharge_threshold = (
            midday_average_price.non_negative() + margin if midday_average_price is not None else margin
        )
        self.appdaemon_logger.log("Discharge threshold: %s", discharge_threshold, level=logging.DEBUG)

        energy_reserve = maximum_cumulative_deficit(hourly_consumptions, hourly_productions)
        self.appdaemon_logger.log("Energy reserve: %s", energy_reserve, level=logging.DEBUG)

        energy_surplus = estimate_battery_surplus_energy(
            energy_reserve,
            state.battery_soc,
            self.configuration.battery_capacity,
            self.configuration.battery_reserve_soc_min,
            self.configuration.battery_reserve_soc_margin,
        )
        self.appdaemon_logger.log("Energy surplus: %s", energy_surplus, level=logging.DEBUG)

        if energy_surplus < self.configuration.battery_export_threshold_energy:
            self.appdaemon_logger.log(
                "Skip, estimated energy surplus %s < threshold %s",
                energy_surplus,
                self.configuration.battery_export_threshold_energy,
                level=logging.DEBUG,
            )
            return None

        energy_to_replenish = estimate_battery_replenish_energy(
            self.configuration.battery_capacity,
            self.configuration.battery_reserve_soc_min,
            self.configuration.battery_reserve_soc_margin,
        )
        self.appdaemon_logger.log("Energy to replenish: %s", energy_to_replenish, level=logging.DEBUG)

        daytime_surplus = total_surplus(daytime_consumptions, daytime_productions)
        self.appdaemon_logger.log("Daytime surplus: %s", daytime_surplus, level=logging.DEBUG)

        if daytime_surplus <= energy_to_replenish:
            self.appdaemon_logger.log(
                "Skip, daytime surplus %s <= energy to replenish %s",
                daytime_surplus,
                energy_to_replenish,
                level=logging.DEBUG,
            )
            return None

        battery_discharge_energy_1h = EnergyKwh(
            self.configuration.battery_maximum_current.value * self.configuration.battery_voltage.value / 1000
        )
        hours = energy_surplus / battery_discharge_energy_1h

        hourly_prices = price_forecast.hourly(discharge_window_start, discharge_window_end)
        revenue_period = find_max_revenue_period(
            hourly_prices,
            discharge_threshold,
            int(hours * 60),
            battery_discharge_energy_1h,
        )

        match revenue_period:
            case (revenue, start, end):
                discharge_slot = BatteryDischargeSlot(
                    start_time=start.time(),
                    end_time=end.time(),
                    current=self.configuration.battery_maximum_current,
                )
                self.appdaemon_logger.log(
                    "Revenue period found: %s, battery discharge slot: %s", revenue, discharge_slot
                )

                return discharge_slot
            case None:
                self.appdaemon_logger.log("Skip, no suitable revenue period found")
                return None
