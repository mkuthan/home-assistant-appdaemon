from datetime import datetime, timedelta

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_soc import BatterySoc
from units.energy_kwh import ENERGY_KWH_ZERO
from utils.battery_estimators import estimate_battery_max_soc, estimate_battery_reserve_soc
from utils.energy_aggregators import maximum_cumulative_deficit, total_surplus


class BatteryReserveSocEstimator:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        config: SolarConfiguration,
        forecast_factory: ForecastFactory,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.config = config
        self.forecast_factory = forecast_factory

    def estimate_soc_tomorrow_at_7_am(self, state: State, now: datetime) -> BatterySoc | None:
        tomorrow_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=1)
        low_tariff_hours = 6

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)

        morning_consumptions = consumption_forecast.hourly(tomorrow_7_am, low_tariff_hours)
        morning_productions = production_forecast.hourly(tomorrow_7_am, low_tariff_hours)

        energy_reserve = maximum_cumulative_deficit(morning_consumptions, morning_productions)
        self.appdaemon_logger.info(f"Energy reserve: {energy_reserve}")

        soc_target = estimate_battery_reserve_soc(
            energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )
        self.appdaemon_logger.info(f"SoC target: {soc_target}")

        if state.battery_reserve_soc >= soc_target:
            self.appdaemon_logger.info(
                f"Skip, battery reserve SoC above target: {state.battery_reserve_soc} >= {soc_target}"
            )
            return None

        return soc_target

    def estimate_soc_today_at_4_pm(self, state: State, now: datetime) -> BatterySoc | None:
        today_4_pm = now.replace(hour=16, minute=0, second=0, microsecond=0)
        low_tariff_hours = 6

        current_hour = now.replace(minute=0, second=0, microsecond=0)
        remaining_hours = today_4_pm.hour - current_hour.hour

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)

        afternoon_consumptions = consumption_forecast.hourly(current_hour, remaining_hours)
        afternoon_productions = production_forecast.hourly(current_hour, remaining_hours)

        energy_surplus = total_surplus(afternoon_consumptions, afternoon_productions)
        self.appdaemon_logger.info(f"Energy surplus: {energy_surplus}")

        evening_consumptions = consumption_forecast.hourly(today_4_pm, low_tariff_hours)
        evening_productions = production_forecast.hourly(today_4_pm, low_tariff_hours)

        evening_deficit = maximum_cumulative_deficit(evening_consumptions, evening_productions)
        self.appdaemon_logger.info(f"Energy deficit: {evening_deficit}")

        energy_reserve = max(evening_deficit - energy_surplus, ENERGY_KWH_ZERO)
        self.appdaemon_logger.info(f"Energy reserve: {energy_reserve}")

        soc_target = estimate_battery_reserve_soc(
            energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )
        self.appdaemon_logger.info(f"SoC target: {soc_target}")

        if state.battery_reserve_soc >= soc_target:
            self.appdaemon_logger.info(
                f"Skip, battery reserve SoC above target: {state.battery_reserve_soc} >= {soc_target}"
            )
            return None

        # Optimization to skip unnecessary Inverter register writes
        if state.battery_soc >= soc_target:
            self.appdaemon_logger.info(f"Skip, battery SoC {state.battery_soc} >= SoC target {soc_target}")
            return None

        soc_solar_only = estimate_battery_max_soc(energy_surplus, state.battery_soc, self.config.battery_capacity)
        if soc_solar_only >= soc_target:
            self.appdaemon_logger.info(f"Skip, estimated SoC max {soc_solar_only} >= SoC target {soc_target}")
            return None

        return soc_target
