from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from solar.storage_mode import StorageMode
from units.battery_soc import BATTERY_SOC_MAX
from units.energy_price import ENERGY_PRICE_ZERO
from utils.battery_estimators import estimate_battery_max_soc
from utils.energy_aggregators import total_surplus


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

    def __call__(self, state: State, period_start: datetime, period_hours: int) -> StorageMode:
        required_battery_reserve_soc = self.config.battery_reserve_soc_min + self.config.battery_reserve_soc_margin
        if state.battery_soc <= required_battery_reserve_soc:
            self.appdaemon_logger.info(
                f"Use {StorageMode.SELF_USE}, battery SoC {state.battery_soc} <= {required_battery_reserve_soc}"
            )
            return StorageMode.SELF_USE

        price_forecast = self.forecast_factory.create_price_forecast(state)
        min_price = price_forecast.find_daily_min_price(period_start, period_hours)
        if min_price is None:
            self.appdaemon_logger.info(f"Use {StorageMode.SELF_USE}, minimum price not found in the forecast")
            return StorageMode.SELF_USE

        current_price = max(state.hourly_price, ENERGY_PRICE_ZERO)
        price_threshold = max(min_price, ENERGY_PRICE_ZERO) + self.config.pv_export_min_price_margin
        if current_price <= price_threshold:
            self.appdaemon_logger.info(
                f"Use {StorageMode.SELF_USE}, current price {current_price} <= {price_threshold}"
            )
            return StorageMode.SELF_USE

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        consumptions = consumption_forecast.hourly(period_start, period_hours)

        production_forecast = self.forecast_factory.create_production_forecast(state)
        productions = production_forecast.hourly(period_start, period_hours)

        energy_surplus = total_surplus(consumptions, productions)
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
