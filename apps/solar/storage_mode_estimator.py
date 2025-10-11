from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from solar.storage_mode import StorageMode
from units.battery_soc import BATTERY_SOC_MAX
from utils.battery_estimators import estimate_battery_max_soc


class StorageModeEstimator:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        config: SolarConfiguration,
        forecast_factory: ForecastFactory,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.config = config
        self.forecast_factory = forecast_factory

    def __call__(self, state: State, now: datetime) -> StorageMode:
        remaining_hours = 24 - now.hour

        if state.battery_soc <= state.battery_reserve_soc:
            self.appdaemon_logger.info(
                f"Battery SoC {state.battery_soc} <= Battery reserve SoC {state.battery_reserve_soc}"
            )
            return StorageMode.SELF_USE

        if state.hourly_price < self.config.pv_export_threshold_price:
            self.appdaemon_logger.info(f"Hourly price {state.hourly_price} < {self.config.pv_export_threshold_price}")
            return StorageMode.SELF_USE

        price_forecast = self.forecast_factory.create_price_forecast(state)
        valley_periods = price_forecast.find_valley_periods(now, remaining_hours, self.config.pv_export_threshold_price)

        if any(p.datetime.hour == now.hour for p in valley_periods):
            self.appdaemon_logger.info(f"Current hour {now.hour} is in valley periods: {valley_periods}")
            return StorageMode.SELF_USE

        production_forecast = self.forecast_factory.create_production_forecast(state)
        production_kwh = production_forecast.estimate_energy_kwh(now, remaining_hours)
        self.appdaemon_logger.info(f"Production forecast: {production_kwh}")

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        consumption_kwh = consumption_forecast.estimate_energy_kwh(now, remaining_hours)
        self.appdaemon_logger.info(f"Consumption forecast: {consumption_kwh}")

        energy_surplus = production_kwh - consumption_kwh
        self.appdaemon_logger.info(f"Energy surplus: {energy_surplus}")

        estimated_battery_max_soc = estimate_battery_max_soc(
            energy_surplus, state.battery_soc, self.config.battery_capacity
        )

        if estimated_battery_max_soc < BATTERY_SOC_MAX:
            self.appdaemon_logger.info(f"Estimated battery max SoC {estimated_battery_max_soc} < {BATTERY_SOC_MAX}")
            return StorageMode.SELF_USE

        self.appdaemon_logger.info(f"No conditions for {StorageMode.SELF_USE} met")
        return StorageMode.FEED_IN_PRIORITY
