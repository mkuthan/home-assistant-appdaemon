from datetime import datetime, timedelta

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_soc import BatterySoc
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

    def estimate_soc_tomorrow_at_7_am(self, state: State, now: datetime, period_hours: int) -> BatterySoc | None:
        tomorrow_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=1)

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)

        morning_consumptions = consumption_forecast.hourly(tomorrow_7_am, period_hours)
        morning_productions = production_forecast.hourly(tomorrow_7_am, period_hours)

        energy_reserve = maximum_cumulative_deficit(morning_consumptions, morning_productions)
        self.appdaemon_logger.info(f"Energy reserve: {energy_reserve}")

        soc_target = estimate_battery_reserve_soc(
            energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )

        if state.battery_reserve_soc >= soc_target:
            self.appdaemon_logger.info(
                f"Skip, battery reserve Soc {state.battery_reserve_soc} >= target SoC {soc_target}"
            )
            return None

        self.appdaemon_logger.info(f"Target SoC: {soc_target}")
        return soc_target

    # TODO: implement tests for this method
    def estimate_soc_today_at_4_pm(self, state: State, now: datetime, period_hours: int) -> BatterySoc | None:
        today_4_pm = now.replace(hour=16, minute=0, second=0, microsecond=0)

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)

        evening_consumptions = consumption_forecast.hourly(today_4_pm, period_hours)
        evening_productions = production_forecast.hourly(today_4_pm, period_hours)

        energy_reserve = maximum_cumulative_deficit(evening_consumptions, evening_productions)
        self.appdaemon_logger.info(f"Energy reserve: {energy_reserve}")

        soc_target = estimate_battery_reserve_soc(
            energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )

        if state.battery_reserve_soc >= soc_target:
            self.appdaemon_logger.info(
                f"Skip, battery reserve Soc {state.battery_reserve_soc} >= target SoC {soc_target}"
            )
            return None

        # Optimization to skip unnecessary Inverter register writes
        if state.battery_soc >= soc_target:
            self.appdaemon_logger.info(f"Skip, battery SoC {state.battery_soc} >= target SoC {soc_target}")
            return None

        current_hour = now.replace(minute=0, second=0, microsecond=0)
        remaining_hours = today_4_pm.hour - current_hour.hour

        afternoon_consumptions = consumption_forecast.hourly(current_hour, remaining_hours)
        afternoon_productions = production_forecast.hourly(current_hour, remaining_hours)

        energy_surplus = total_surplus(afternoon_consumptions, afternoon_productions)
        self.appdaemon_logger.info(f"Energy surplus: {energy_surplus}")

        soc_solar_only = estimate_battery_max_soc(energy_surplus, state.battery_soc, self.config.battery_capacity)
        if soc_solar_only >= soc_target:
            self.appdaemon_logger.info(f"Skip, estimated SoC {soc_solar_only} >= target SoC {soc_target}")
            return None

        soc_grid_charging = soc_target - soc_solar_only
        self.appdaemon_logger.info(
            f"Target SoC after surplus energy alignment: {soc_grid_charging}, original target SoC: {soc_target}"
        )
        return soc_grid_charging
