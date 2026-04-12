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
from utils.adjusters import adjust_energy_surplus, adjust_export_threshold_price
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

        tomorrow_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_hours = 24

        tomorrow_10_30_am = (now + timedelta(days=1)).replace(hour=10, minute=30, second=0, microsecond=0)
        midday_hours = 4

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)
        price_forecast = self.forecast_factory.create_price_forecast(state)

        hourly_consumptions = consumption_forecast.hourly(today_4_pm, low_tariff_hours)
        hourly_productions = production_forecast.hourly(today_4_pm, low_tariff_hours)
        production_forecast_total = production_forecast.total(tomorrow_midnight, tomorrow_hours)
        midday_average_price = price_forecast.average_price(tomorrow_10_30_am, midday_hours)

        return self._estimate_battery_discharge_slot(
            state,
            hourly_consumptions,
            hourly_productions,
            production_forecast_total,
            midday_average_price,
            price_forecast,
            today_4_pm,
            today_10_pm,
        )

    def estimate_battery_discharge_at_6_am(self, state: SolarState, now: datetime) -> BatteryDischargeSlot | None:
        today_6_am = now.replace(hour=6, minute=0, second=0, microsecond=0)
        today_9_am = now.replace(hour=9, minute=0, second=0, microsecond=0)
        morning_hours = 3

        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_hours = 24

        today_10_30_am = now.replace(hour=10, minute=30, second=0, microsecond=0)
        midday_hours = 4

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)
        price_forecast = self.forecast_factory.create_price_forecast(state)

        hourly_consumptions = consumption_forecast.hourly(today_6_am, morning_hours)
        hourly_productions = production_forecast.hourly(today_6_am, morning_hours)
        production_forecast_total = production_forecast.total(today_midnight, today_hours)
        midday_average_price = price_forecast.average_price(today_10_30_am, midday_hours)

        return self._estimate_battery_discharge_slot(
            state,
            hourly_consumptions,
            hourly_productions,
            production_forecast_total,
            midday_average_price,
            price_forecast,
            today_6_am,
            today_9_am,
        )

    def _estimate_battery_discharge_slot(
        self,
        state: SolarState,
        hourly_consumptions: list[HourlyConsumptionEnergy],
        hourly_productions: list[HourlyProductionEnergy],
        production_forecast_total: EnergyKwh,
        midday_average_price: EnergyPrice | None,
        price_forecast: PriceForecast,
        discharge_window_start: datetime,
        discharge_window_end: datetime,
    ) -> BatteryDischargeSlot | None:
        self.appdaemon_logger.log(
            "Battery export threshold price: %s", self.configuration.battery_export_threshold_price, level=logging.DEBUG
        )

        adjusted_battery_export_threshold_price = adjust_export_threshold_price(
            self.configuration.battery_export_threshold_price,
            self.configuration.pv_export_threshold_price,
            midday_average_price,
            production_forecast_total,
            self.configuration.installation_capacity,
        )
        self.appdaemon_logger.log(
            "Adjusted battery export threshold price: %s", adjusted_battery_export_threshold_price, level=logging.DEBUG
        )

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

        adjusted_energy_surplus = adjust_energy_surplus(
            energy_surplus,
            self.configuration.battery_export_threshold_price,
            adjusted_battery_export_threshold_price,
        )
        self.appdaemon_logger.log("Adjusted energy surplus: %s", adjusted_energy_surplus, level=logging.DEBUG)

        if adjusted_energy_surplus < self.configuration.battery_export_threshold_energy:
            self.appdaemon_logger.log(
                "Skip, estimated adjusted energy surplus %s < threshold %s",
                adjusted_energy_surplus,
                self.configuration.battery_export_threshold_energy,
                level=logging.DEBUG,
            )
            return None

        battery_discharge_energy_1h = EnergyKwh(
            self.configuration.battery_maximum_current.value * self.configuration.battery_voltage.value / 1000
        )
        hours = adjusted_energy_surplus / battery_discharge_energy_1h

        hourly_prices = price_forecast.hourly(discharge_window_start, discharge_window_end)
        revenue_period = find_max_revenue_period(
            hourly_prices,
            adjusted_battery_export_threshold_price,
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
