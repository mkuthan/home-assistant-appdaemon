from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.battery_discharge_slot import BatteryDischargeSlot
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_current import BATTERY_CURRENT_ZERO
from utils.battery_converters import current_to_energy, energy_to_current
from utils.battery_estimators import estimate_battery_surplus_energy
from utils.energy_aggregators import maximum_cumulative_deficit


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

    def estimate_battery_discharge_at_4_pm(self, state: SolarState, now: datetime) -> list[BatteryDischargeSlot]:
        today_4_pm = now.replace(hour=16, minute=0, second=0, microsecond=0)
        low_tariff_hours = 6

        price_forecast = self.forecast_factory.create_price_forecast(state)
        peak_periods = price_forecast.find_peak_periods(
            today_4_pm, low_tariff_hours, self.configuration.battery_export_threshold_price
        )
        if not peak_periods:
            self.appdaemon_logger.log(
                "Skip, no peak periods above the threshold %s found in the price forecast",
                self.configuration.battery_export_threshold_price,
            )
            return []

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

        battery_discharge_current = energy_to_current(energy_surplus, self.configuration.battery_voltage)
        self.appdaemon_logger.log("Battery discharge current: %s", battery_discharge_current)

        sorted_peak_periods = sorted(peak_periods, key=lambda period: period.price.value, reverse=True)

        discharge_slots = []
        remaining_current = battery_discharge_current

        for period in sorted_peak_periods:
            if remaining_current == BATTERY_CURRENT_ZERO:
                break

            slot_current = min(remaining_current, self.configuration.battery_maximum_current)

            slot_energy = current_to_energy(slot_current, self.configuration.battery_voltage, duration_hours=1)
            if slot_energy <= self.configuration.battery_export_threshold_energy:
                self.appdaemon_logger.log(
                    "Skip slot %s, estimated energy %s <= %s",
                    period,
                    slot_energy,
                    self.configuration.battery_export_threshold_energy,
                )
                continue

            discharge_slot = BatteryDischargeSlot(
                start_time=period.period.start_time(),
                end_time=period.period.end_time(),
                current=round(slot_current),
            )
            discharge_slots.append(discharge_slot)
            self.appdaemon_logger.log("Battery discharge slot: %s", discharge_slot)

            remaining_current = remaining_current - slot_current

        return discharge_slots
