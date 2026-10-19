from datetime import datetime
from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from solar.consumption_forecast import (
    ConsumptionForecast,
    ConsumptionForecastComposite,
    ConsumptionForecastHvacHeating,
    ConsumptionForecastRegular,
)
from solar.price_forecast import PriceForecast
from solar.production_forecast import ProductionForecast, ProductionForecastComposite, ProductionForecastDefault
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.weather_forecast import WeatherForecast
from utils.sensor_publisher import SensorPublisher


class ForecastFactory(Protocol):
    def create_production_forecast(self, state: SolarState) -> ProductionForecast: ...
    def create_consumption_forecast(self, state: SolarState, now: datetime) -> ConsumptionForecast: ...
    def create_price_forecast(self, state: SolarState) -> PriceForecast: ...
    def create_weather_forecast(self, state: SolarState) -> WeatherForecast: ...


class DefaultForecastFactory:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        sensor_publisher: SensorPublisher,
        configuration: SolarConfiguration,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.sensor_publisher = sensor_publisher
        self.configuration = configuration

    def create_production_forecast(self, state: SolarState) -> ProductionForecast:
        today = ProductionForecastDefault.create(state.pv_forecast_today)
        tomorrow = ProductionForecastDefault.create(state.pv_forecast_tomorrow)

        return ProductionForecastComposite(today, tomorrow)

    def create_consumption_forecast(self, state: SolarState, now: datetime) -> ConsumptionForecast:
        weather_forecast = self.create_weather_forecast(state)

        regular = ConsumptionForecastRegular(
            is_away_mode=state.is_away_mode or False,
            consumption_away=self.configuration.regular_consumption_away,
            consumption_day=self.configuration.regular_consumption_day,
            consumption_evening=self.configuration.regular_consumption_evening,
        )

        hvac_heating = ConsumptionForecastHvacHeating(
            now=now,
            forecast_weather=weather_forecast,
            hvac_heating_mode=state.hvac_heating_mode,
            t_in=self.configuration.temp_in,
            t_in_actual=state.indoor_temperature,
            t_in_target=state.hvac_heating_temperature,
            cop_at_7c=self.configuration.heating_cop_at_7c,
            h=self.configuration.heating_h,
            decay_rate=self.configuration.heating_decay_rate,
            temp_out_fallback=self.configuration.temp_out_fallback,
            humidity_out_fallback=self.configuration.humidity_out_fallback,
            sensor_publisher=self.sensor_publisher,
        )

        return ConsumptionForecastComposite(regular, hvac_heating)

    def create_price_forecast(self, state: SolarState) -> PriceForecast:
        raw_forecast = (state.price_forecast_today or []) + (state.price_forecast_tomorrow or [])
        return PriceForecast.create_from_rce_15_mins(raw_forecast, self.configuration.time_zone)

    def create_weather_forecast(self, state: SolarState) -> WeatherForecast:
        return WeatherForecast.create(state.weather_forecast)
