from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_soc import BatterySoc
from utils.battery_estimators import estimate_battery_reserve_soc


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

    def __call__(self, state: State, period_start: datetime, period_hours: int) -> BatterySoc | None:
        production_forecast = self.forecast_factory.create_production_forecast(state)
        production_kwh = production_forecast.estimate_energy_kwh(period_start, period_hours)
        self.appdaemon_logger.info(f"Production forecast: {production_kwh}")

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        consumption_kwh = consumption_forecast.estimate_energy_kwh(period_start, period_hours)
        self.appdaemon_logger.info(f"Consumption forecast: {consumption_kwh}")

        energy_reserve = consumption_kwh - production_kwh
        self.appdaemon_logger.info(f"Required energy reserve: {energy_reserve}")

        estimated_reserve_soc = estimate_battery_reserve_soc(
            energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
        )

        if estimated_reserve_soc <= state.battery_reserve_soc:
            self.appdaemon_logger.info(
                f"Estimated reserve SoC: {estimated_reserve_soc} <= current reserve SoC: {state.battery_reserve_soc}"
            )
            return None

        self.appdaemon_logger.info(f"Estimated reserve SoC: {estimated_reserve_soc}")
        return estimated_reserve_soc
