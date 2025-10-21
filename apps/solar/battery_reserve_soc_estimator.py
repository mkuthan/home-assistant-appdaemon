from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.forecast_factory import ForecastFactory
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_soc import BatterySoc
from units.hourly_energy import HourlyEnergyAggregator
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
        hourly_productions = production_forecast.hourly(period_start, period_hours)
        self.appdaemon_logger.info(f"Hourly productions: {hourly_productions}")

        consumption_forecast = self.forecast_factory.create_consumption_forecast(state)
        hourly_consumptions = consumption_forecast.hourly(period_start, period_hours)
        self.appdaemon_logger.info(f"Hourly consumptions: {hourly_consumptions}")

        hourly_nets = HourlyEnergyAggregator.aggregate_hourly_net(hourly_consumptions, hourly_productions)
        self.appdaemon_logger.info(f"Hourly nets: {hourly_nets}")

        required_energy_reserve = HourlyEnergyAggregator.maximum_cumulative_deficit(hourly_nets)
        self.appdaemon_logger.info(f"Required energy reserve: {required_energy_reserve}")

        estimated_reserve_soc = estimate_battery_reserve_soc(
            required_energy_reserve,
            self.config.battery_capacity,
            self.config.battery_reserve_soc_min,
            self.config.battery_reserve_soc_margin,
            self.config.battery_reserve_soc_max,
        )

        if estimated_reserve_soc <= state.battery_reserve_soc:
            self.appdaemon_logger.info(
                f"Estimated battery reserve SoC: {estimated_reserve_soc} <= "
                + f"current battery reserve SoC: {state.battery_reserve_soc}"
            )
            return None

        self.appdaemon_logger.info(f"Estimated battery reserve SoC: {estimated_reserve_soc}")
        return estimated_reserve_soc
