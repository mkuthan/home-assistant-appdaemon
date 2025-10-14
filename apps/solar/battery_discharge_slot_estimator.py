from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_discharge_slot import BatteryDischargeSlot
from utils.battery_estimators import estimate_battery_surplus_energy


class BatteryDischargeSlotEstimator:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        config: SolarConfiguration,
        forecast_factory: ForecastFactory,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.config = config
        self.forecast_factory = forecast_factory

    def __call__(self, state: State, period_start: datetime, period_hours: int) -> list[BatteryDischargeSlot]:
        price_forecast = self.forecast_factory.create_price_forecast(state)
        peak_periods = price_forecast.find_peak_periods(
            period_start, period_hours, self.config.battery_export_threshold_price
        )
        if not peak_periods:
            self.appdaemon_logger.info(
                f"No peak periods above the threshold {self.config.battery_export_threshold_price} "
                + "found in the price forecast"
            )
            return []

        best_period = max(peak_periods, key=lambda period: period.price.value)
        self.appdaemon_logger.info(f"Best peak period: {best_period}")

        production_forecast = self.forecast_factory.create_production_forecast(state)
        production_kwh = production_forecast.estimate_energy_kwh(period_start, period_hours)
        self.appdaemon_logger.info(f"Production forecast: {production_kwh}")

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        consumption_kwh = consumption_forecast.estimate_energy_kwh(period_start, period_hours)
        self.appdaemon_logger.info(f"Consumption forecast: {consumption_kwh}")

        energy_reserve = consumption_kwh - production_kwh
        self.appdaemon_logger.info(f"Required energy reserve: {energy_reserve}")

        estimated_surplus_energy = estimate_battery_surplus_energy(
            energy_reserve,
            state.battery_soc,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
        )
        if estimated_surplus_energy <= self.config.battery_export_threshold_energy:
            self.appdaemon_logger.info(
                f"Estimated surplus energy {estimated_surplus_energy} "
                + f"is below the threshold {self.config.battery_export_threshold_energy}"
            )
            return []

        self.appdaemon_logger.info(f"Estimated surplus energy: {estimated_surplus_energy}")

        estimated_discharge_current = estimated_surplus_energy.to_battery_current(self.config.battery_voltage)
        self.appdaemon_logger.info(f"Estimated battery discharge current: {estimated_discharge_current}")

        discharge_slot = BatteryDischargeSlot(
            start_time=best_period.start_time(),
            end_time=best_period.end_time(),
            current=min(estimated_discharge_current, self.config.battery_maximum_current),
        )

        self.appdaemon_logger.info(f"Estimated battery discharge slot: {discharge_slot}")
        return [discharge_slot]
