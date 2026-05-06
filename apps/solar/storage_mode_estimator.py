import logging
from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.storage_mode import StorageMode
from utils.battery_estimators import estimate_battery_energy_gap_to_full
from utils.energy_aggregators import total_surplus
from utils.time_utils import truncate_to_hour


class StorageModeEstimator:
    _FEED_IN_PRIORITY_END_HOUR: int = 12
    _BATTERY_FULL_BY_HOUR: int = 15

    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: SolarConfiguration,
        forecast_factory: ForecastFactory,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration
        self.forecast_factory = forecast_factory

    def estimate_storage_mode(self, state: SolarState, now: datetime) -> StorageMode | None:
        if now.hour >= self._FEED_IN_PRIORITY_END_HOUR:
            reason = "past feed-in priority end hour"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        required_battery_reserve_soc = (
            self.configuration.battery_reserve_soc_min + self.configuration.battery_reserve_soc_margin
        )
        current_battery_soc = state.battery_soc

        if current_battery_soc < required_battery_reserve_soc:
            reason = f"battery SoC {current_battery_soc} < {required_battery_reserve_soc}"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        today_8_am = now.replace(hour=8, minute=0, second=0, microsecond=0)
        day_hours = 8

        price_forecast = self.forecast_factory.create_price_forecast(state)
        min_price = price_forecast.find_min_hour(today_8_am, day_hours)
        if min_price is None:
            reason = "minimum price not found in the forecast"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        price_threshold = max(min_price.price.non_negative(), self.configuration.pv_export_threshold_price)
        current_price = state.hourly_price.non_negative()
        if current_price < price_threshold:
            reason = f"price {current_price} < {price_threshold}"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        current_hour = truncate_to_hour(now)
        remaining_hours = self._BATTERY_FULL_BY_HOUR - now.hour

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        remaining_consumptions = consumption_forecast.hourly(current_hour, remaining_hours)

        production_forecast = self.forecast_factory.create_production_forecast(state)
        remaining_productions = production_forecast.hourly(current_hour, remaining_hours)

        remaining_surplus = total_surplus(remaining_consumptions, remaining_productions)

        battery_gap_to_full = estimate_battery_energy_gap_to_full(
            current_battery_soc, self.configuration.battery_capacity
        )

        if remaining_surplus < battery_gap_to_full:
            reason = f"remaining surplus: {remaining_surplus} < battery gap to full: {battery_gap_to_full}"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        reason = (
            f"current price: {current_price}, threshold price: {price_threshold}, "
            + f"battery gap to full: {battery_gap_to_full}, remaining surplus: {remaining_surplus}"
        )
        return self._return_if_changed(state, StorageMode.FEED_IN_PRIORITY, reason)

    def _return_if_changed(self, state: SolarState, storage_mode: StorageMode, reason: str) -> StorageMode | None:
        if storage_mode != state.inverter_storage_mode:
            self.appdaemon_logger.log("Use %s, %s", storage_mode, reason, level=logging.DEBUG)
            return storage_mode
        else:
            self.appdaemon_logger.log("Skip, storage mode unchanged: %s, %s", storage_mode, reason, level=logging.DEBUG)
            return None
