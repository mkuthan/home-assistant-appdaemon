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
from utils.battery_estimators import estimate_battery_energy_to_full, estimate_battery_surplus_energy
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

        evening_consumptions = consumption_forecast.hourly(today_4_pm, high_tariff_hours)
        evening_productions = production_forecast.hourly(today_4_pm, high_tariff_hours)
        daytime_consumptions = consumption_forecast.hourly(tomorrow_7_am, daytime_hours)
        daytime_productions = production_forecast.hourly(tomorrow_7_am, daytime_hours)
        midday_average_price = price_forecast.average_price(tomorrow_10_30_am, midday_hours)

        return self._estimate_battery_discharge_slot(
            state,
            self.configuration.battery_discharge_evening_margin,
            evening_consumptions,
            evening_productions,
            daytime_consumptions,
            daytime_productions,
            midday_average_price,
            price_forecast,
            today_4_pm,
            today_10_pm,
        )

    def estimate_battery_discharge_at_6_am(self, state: SolarState, now: datetime) -> BatteryDischargeSlot | None:
        today_6_am = now.replace(hour=6, minute=0, second=0, microsecond=0)
        today_9_am = now.replace(hour=9, minute=0, second=0, microsecond=0)

        today_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0)
        high_tariff_hours = 6

        today_10_30_am = now.replace(hour=10, minute=30, second=0, microsecond=0)
        midday_hours = 4

        daytime_hours = 9

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)
        price_forecast = self.forecast_factory.create_price_forecast(state)

        morning_consumptions = consumption_forecast.hourly(today_7_am, high_tariff_hours)
        morning_productions = production_forecast.hourly(today_7_am, high_tariff_hours)
        daytime_consumptions = consumption_forecast.hourly(today_7_am, daytime_hours)
        daytime_productions = production_forecast.hourly(today_7_am, daytime_hours)
        midday_average_price = price_forecast.average_price(today_10_30_am, midday_hours)

        return self._estimate_battery_discharge_slot(
            state,
            self.configuration.battery_discharge_morning_margin,
            morning_consumptions,
            morning_productions,
            daytime_consumptions,
            daytime_productions,
            midday_average_price,
            price_forecast,
            today_6_am,
            today_9_am,
        )

    def _estimate_battery_discharge_slot(
        self,
        state: SolarState,
        margin: EnergyPrice,
        high_tariff_consumptions: list[HourlyConsumptionEnergy],
        high_tariff_productions: list[HourlyProductionEnergy],
        daytime_consumptions: list[HourlyConsumptionEnergy],
        daytime_productions: list[HourlyProductionEnergy],
        midday_average_price: EnergyPrice | None,
        price_forecast: PriceForecast,
        discharge_window_start: datetime,
        discharge_window_end: datetime,
    ) -> BatteryDischargeSlot | None:
        high_tariff_reserve = maximum_cumulative_deficit(high_tariff_consumptions, high_tariff_productions)
        self.appdaemon_logger.log("High tariff reserve: %s", high_tariff_reserve, level=logging.DEBUG)

        high_tariff_surplus = estimate_battery_surplus_energy(
            high_tariff_reserve,
            state.battery_soc,
            self.configuration.battery_capacity,
            self.configuration.battery_reserve_soc_min,
            self.configuration.battery_reserve_soc_margin,
        )
        self.appdaemon_logger.log("High tariff surplus: %s", high_tariff_surplus, level=logging.DEBUG)

        if high_tariff_surplus < self.configuration.battery_export_threshold_energy:
            self.appdaemon_logger.log(
                "Skip, high tariff surplus %s < threshold %s",
                high_tariff_surplus,
                self.configuration.battery_export_threshold_energy,
                level=logging.DEBUG,
            )
            return None

        daytime_surplus = total_surplus(daytime_consumptions, daytime_productions)
        self.appdaemon_logger.log("Daytime surplus: %s", daytime_surplus, level=logging.DEBUG)

        energy_to_battery_replenish = estimate_battery_energy_to_full(
            self.configuration.battery_capacity,
            self.configuration.battery_reserve_soc_min,
            self.configuration.battery_reserve_soc_margin,
        )

        if daytime_surplus <= energy_to_battery_replenish:
            self.appdaemon_logger.log(
                "Skip, daytime surplus %s <= energy to battery replenish %s",
                daytime_surplus,
                energy_to_battery_replenish,
                level=logging.DEBUG,
            )
            return None

        hourly_prices = price_forecast.hourly(discharge_window_start, discharge_window_end)

        price_threshold = midday_average_price.non_negative() + margin if midday_average_price is not None else margin

        battery_discharge_energy_1h = EnergyKwh(
            self.configuration.battery_maximum_current.value * self.configuration.battery_voltage.value / 1000
        )
        hours = high_tariff_surplus / battery_discharge_energy_1h

        revenue_period = find_max_revenue_period(
            hourly_prices,
            price_threshold,
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
                    "Price threshold: %s, revenue: %s, battery discharge slot: %s",
                    price_threshold,
                    revenue,
                    discharge_slot,
                )

                return discharge_slot
            case None:
                self.appdaemon_logger.log("Skip, no suitable revenue for price threshold %s", price_threshold)
                return None
