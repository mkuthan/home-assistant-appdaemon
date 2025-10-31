from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.storage_mode import StorageMode
from units.battery_soc import BATTERY_SOC_MAX
from utils.battery_estimators import estimate_battery_max_soc
from utils.energy_aggregators import total_surplus


class StorageModeEstimator:
    END_HOUR: int = 16

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
        remaining_hours = self.END_HOUR - now.hour
        if remaining_hours <= 0:
            reason = "no remaining hours in the day"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        price_forecast = self.forecast_factory.create_price_forecast(state)
        min_price = price_forecast.find_daily_min_price(now, remaining_hours)
        if min_price is None:
            reason = "minimum price not found in the forecast"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        current_price = state.hourly_price.non_negative()
        price_threshold = min_price.non_negative() + self.configuration.pv_export_min_price_margin
        if current_price <= price_threshold:
            reason = f"current price {current_price} <= {price_threshold}"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        required_battery_reserve_soc = (
            self.configuration.battery_reserve_soc_min + self.configuration.battery_reserve_soc_margin
        )
        if state.battery_soc <= required_battery_reserve_soc:
            reason = f"battery SoC {state.battery_soc} <= {required_battery_reserve_soc}"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        consumptions = consumption_forecast.hourly(now, remaining_hours)

        production_forecast = self.forecast_factory.create_production_forecast(state)
        productions = production_forecast.hourly(now, remaining_hours)

        energy_surplus = total_surplus(consumptions, productions)

        battery_soc_max = estimate_battery_max_soc(
            energy_surplus, state.battery_soc, self.configuration.battery_capacity
        )

        if battery_soc_max < BATTERY_SOC_MAX:
            reason = f"battery SoC max {battery_soc_max} < {BATTERY_SOC_MAX}, energy surplus: {energy_surplus}"
            return self._return_if_changed(state, StorageMode.SELF_USE, reason)

        reason = f"current price: {current_price}, current battery SoC: {state.battery_soc}"
        return self._return_if_changed(state, StorageMode.FEED_IN_PRIORITY, reason)

    def _return_if_changed(self, state: SolarState, storage_mode: StorageMode, reason: str) -> StorageMode | None:
        if storage_mode != state.inverter_storage_mode:
            self.appdaemon_logger.info(f"Use {StorageMode.SELF_USE}, {reason}")
            return storage_mode
        else:
            return None
