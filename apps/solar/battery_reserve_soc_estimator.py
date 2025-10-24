from datetime import datetime, timedelta

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_soc import BatterySoc
from utils.battery_estimators import estimate_battery_max_soc, estimate_battery_reserve_soc, estimate_time_to_charge
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

    def estimate_soc_tomorrow_at_7_am(self, state: State, now: datetime, period_hours: int = 6) -> BatterySoc | None:
        tomorrow_7_am = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=1)

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)

        morning_consumptions = consumption_forecast.hourly(tomorrow_7_am, period_hours)
        morning_productions = production_forecast.hourly(tomorrow_7_am, period_hours)

        required_energy_reserve = maximum_cumulative_deficit(morning_consumptions, morning_productions)

        soc_target = estimate_battery_reserve_soc(
            required_energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )

        if soc_target <= state.battery_reserve_soc:
            # Target SoC already set
            return None
        else:
            # Disallow battery discharge to keep target SoC or start charging to reach target SoC
            return soc_target

    def estimate_soc_today_at_4_pm(self, state: State, now: datetime, period_hours: int = 6) -> BatterySoc | None:
        today_4_pm = now.replace(hour=16, minute=0, second=0, microsecond=0)

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        production_forecast = self.forecast_factory.create_production_forecast(state)

        evening_consumptions = consumption_forecast.hourly(today_4_pm, period_hours)
        evening_productions = production_forecast.hourly(today_4_pm, period_hours)

        required_energy_reserve = maximum_cumulative_deficit(evening_consumptions, evening_productions)

        soc_target = estimate_battery_reserve_soc(
            required_energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )

        if soc_target <= state.battery_soc:
            # Target SoC already reached
            return None

        current_hour = now.replace(minute=0, second=0, microsecond=0)
        remaining_hours = today_4_pm.hour - current_hour.hour

        afternoon_consumptions = consumption_forecast.hourly(current_hour, remaining_hours)
        afternoon_productions = production_forecast.hourly(current_hour, remaining_hours)

        surplus_energy = total_surplus(afternoon_consumptions, afternoon_productions)

        soc_solar_only = estimate_battery_max_soc(surplus_energy, state.battery_soc, self.config.battery_capacity)
        if soc_solar_only >= soc_target:
            # Can reach target SoC with solar production only
            return None

        soc_deficit = soc_target - soc_solar_only
        remaining_time = today_4_pm - now
        time_to_charge = estimate_time_to_charge(
            soc_deficit,
            self.config.battery_capacity,
            self.config.battery_maximum_current,
            self.config.battery_voltage,
        )
        safety_margin = timedelta(minutes=30)
        if remaining_time > time_to_charge + safety_margin:
            # Can reach target SoC with solar production and grid charging
            # Prevent battery discharging below current SoC
            return state.battery_soc
        else:
            # Start charging to reach target SoC
            return soc_target

    def __call__(self, state: State, period_start: datetime, period_hours: int) -> BatterySoc | None:
        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        hourly_consumptions = consumption_forecast.hourly(period_start, period_hours)

        production_forecast = self.forecast_factory.create_production_forecast(state)
        hourly_productions = production_forecast.hourly(period_start, period_hours)

        required_energy_reserve = maximum_cumulative_deficit(hourly_consumptions, hourly_productions)
        self.appdaemon_logger.info(f"Required energy reserve: {required_energy_reserve}")

        battery_reserve_soc_target = estimate_battery_reserve_soc(
            required_energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )

        if battery_reserve_soc_target <= state.battery_reserve_soc:
            self.appdaemon_logger.info(
                f"Battery reserve SoC target: {battery_reserve_soc_target} <= "
                + f"current battery reserve SoC: {state.battery_reserve_soc}"
            )
            return None

        self.appdaemon_logger.info(f"Battery reserve SoC target: {battery_reserve_soc_target}")
        return battery_reserve_soc_target
