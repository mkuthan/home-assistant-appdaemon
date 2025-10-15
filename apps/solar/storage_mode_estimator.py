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

    def __call__(self, state: State, now: datetime, period_hours: int) -> StorageMode:
        required_battery_reserve_soc = self.config.battery_reserve_soc_min + self.config.battery_reserve_soc_margin
        if state.battery_soc <= required_battery_reserve_soc:
            self.appdaemon_logger.info(
                f"Use {StorageMode.SELF_USE}, battery SoC {state.battery_soc} <= {required_battery_reserve_soc}"
            )
            return StorageMode.SELF_USE

        price_forecast = self.forecast_factory.create_price_forecast(state)
        min_price = price_forecast.find_daily_min_price(now, period_hours)
        if min_price is None:
            self.appdaemon_logger.info(f"Use {StorageMode.SELF_USE}, minimum price not found in the forecast")
            return StorageMode.SELF_USE

        current_price = state.hourly_price.max_with_zero()
        price_threshold = min_price.max_with_zero() + self.config.pv_export_min_price_margin
        if current_price <= price_threshold:
            self.appdaemon_logger.info(
                f"Use {StorageMode.SELF_USE}, current price {current_price} <= {price_threshold}"
            )
            return StorageMode.SELF_USE

        production_forecast = self.forecast_factory.create_production_forecast(state)
        production_kwh = production_forecast.estimate_energy_kwh(now, period_hours)
        self.appdaemon_logger.info(f"Production forecast: {production_kwh}")

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        consumption_kwh = consumption_forecast.estimate_energy_kwh(now, period_hours)
        self.appdaemon_logger.info(f"Consumption forecast: {consumption_kwh}")

        energy_surplus = production_kwh - consumption_kwh
        self.appdaemon_logger.info(f"Energy surplus: {energy_surplus}")

        estimated_battery_max_soc = estimate_battery_max_soc(
            energy_surplus, state.battery_soc, self.config.battery_capacity
        )

        if estimated_battery_max_soc < BATTERY_SOC_MAX:
            self.appdaemon_logger.info(
                f"Use {StorageMode.SELF_USE}, estimated battery max SoC {estimated_battery_max_soc} < {BATTERY_SOC_MAX}"
            )
            return StorageMode.SELF_USE

        self.appdaemon_logger.info(
            f"Use {StorageMode.FEED_IN_PRIORITY}, current price: {current_price}, "
            + f"current battery SoC: {state.battery_soc}"
        )

        return StorageMode.FEED_IN_PRIORITY
