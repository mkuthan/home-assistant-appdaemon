from datetime import datetime, timedelta

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_soc import BatterySoc
from units.energy_kwh import ENERGY_KWH_ZERO
from utils.battery_estimators import estimate_battery_max_soc, estimate_battery_reserve_soc
from utils.energy_aggregators import maximum_cumulative_deficit, total_surplus
from utils.time_utils import hours_difference, is_time_in_range, truncate_to_hour


class BatteryReserveSocEstimator:
    _HOURS_BEFORE_TARGET_ESTIMATION = 2

    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        configuration: SolarConfiguration,
        forecast_factory: ForecastFactory,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.configuration = configuration
        self.forecast_factory = forecast_factory

    def estimate_battery_reserve_soc(self, state: SolarState, now: datetime) -> BatterySoc | None:
        is_night_low_tariff = is_time_in_range(
            now.time(), self.configuration.night_low_tariff_time_start, self.configuration.night_low_tariff_time_end
        )
        is_day_low_tariff = is_time_in_range(
            now.time(), self.configuration.day_low_tariff_time_start, self.configuration.day_low_tariff_time_end
        )

        if is_night_low_tariff:
            next_high_tariff_hours = hours_difference(
                self.configuration.night_low_tariff_time_end, self.configuration.day_low_tariff_time_start
            )
            battery_reserve_soc_target = self._estimate_soc_at_7_am(state, now, next_high_tariff_hours)
        elif is_day_low_tariff:
            next_high_tariff_hours = hours_difference(
                self.configuration.day_low_tariff_time_end, self.configuration.night_low_tariff_time_start
            )
            battery_reserve_soc_target = self._estimate_soc_at_4_pm(state, now, next_high_tariff_hours)
        else:
            battery_reserve_soc_target = self.configuration.battery_reserve_soc_min

        battery_reserve_soc_target = round(battery_reserve_soc_target)

        if battery_reserve_soc_target != state.battery_reserve_soc:
            self.appdaemon_logger.log("Battery reserve SoC target: %s", battery_reserve_soc_target)
            return battery_reserve_soc_target
        else:
            return None

    def _estimate_soc_at_7_am(self, state: SolarState, now: datetime, next_high_tariff_hours: int) -> BatterySoc:
        if now.hour >= 7:
            upcoming_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            upcoming_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0)

        if upcoming_7_am - now < timedelta(hours=self._HOURS_BEFORE_TARGET_ESTIMATION):
            consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
            production_forecast = self.forecast_factory.create_production_forecast(state)

            morning_consumptions = consumption_forecast.hourly(upcoming_7_am, next_high_tariff_hours)
            morning_productions = production_forecast.hourly(upcoming_7_am, next_high_tariff_hours)
            energy_reserve = maximum_cumulative_deficit(morning_consumptions, morning_productions)
        else:
            energy_reserve = ENERGY_KWH_ZERO

        battery_reserve_soc_target = estimate_battery_reserve_soc(
            energy_reserve,
            self.configuration.battery_capacity,
            self.configuration.battery_reserve_soc_min,
            self.configuration.battery_reserve_soc_margin,
            self.configuration.battery_reserve_soc_max,
        )

        # Don't set the battery reserve SoC target below the current value
        battery_reserve_soc_target = max(battery_reserve_soc_target, state.battery_reserve_soc)

        return round(battery_reserve_soc_target)

    def _estimate_soc_at_4_pm(self, state: SolarState, now: datetime, next_high_tariff_hours: int) -> BatterySoc:
        if now.hour >= 16:
            upcoming_4_pm = now.replace(hour=16, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            upcoming_4_pm = now.replace(hour=16, minute=0, second=0, microsecond=0)

        current_hour = truncate_to_hour(now)
        remaining_hours = upcoming_4_pm.hour - current_hour.hour

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)

        remaining_consumptions = consumption_forecast.hourly(current_hour, remaining_hours)
        remaining_productions = production_forecast.hourly(current_hour, remaining_hours)

        energy_surplus = total_surplus(remaining_consumptions, remaining_productions)

        if upcoming_4_pm - now < timedelta(hours=self._HOURS_BEFORE_TARGET_ESTIMATION):
            evening_consumptions = consumption_forecast.hourly(upcoming_4_pm, next_high_tariff_hours)
            evening_productions = production_forecast.hourly(upcoming_4_pm, next_high_tariff_hours)

            evening_deficit = maximum_cumulative_deficit(evening_consumptions, evening_productions)
        else:
            evening_deficit = ENERGY_KWH_ZERO

        energy_reserve = max(evening_deficit - energy_surplus, ENERGY_KWH_ZERO)

        battery_reserve_soc_target = estimate_battery_reserve_soc(
            energy_reserve,
            self.configuration.battery_capacity,
            self.configuration.battery_reserve_soc_min,
            self.configuration.battery_reserve_soc_margin,
            self.configuration.battery_reserve_soc_max,
        )

        # Don't set the battery reserve SoC target below the current value
        battery_reserve_soc_target = max(battery_reserve_soc_target, state.battery_reserve_soc)

        # Skip unnecessary Inverter register writes
        if state.battery_soc >= battery_reserve_soc_target:
            return state.battery_reserve_soc

        # Skip unnecessary grid charging
        battery_soc_solar_only = estimate_battery_max_soc(
            energy_surplus, state.battery_soc, self.configuration.battery_capacity
        )
        if battery_soc_solar_only >= battery_reserve_soc_target:
            return state.battery_reserve_soc

        return round(battery_reserve_soc_target)
