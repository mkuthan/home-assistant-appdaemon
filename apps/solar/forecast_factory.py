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
from solar.state import State
from solar.weather_forecast import WeatherForecast


class ForecastFactory(Protocol):
    def create_production_forecast(self, state: State) -> ProductionForecast: ...
    def create_consumption_forecast(self, state: State) -> ConsumptionForecast: ...
    def create_price_forecast(self, state: State) -> PriceForecast: ...
    def create_weather_forecast(self, state: State) -> WeatherForecast: ...


class DefaultForecastFactory:
    def __init__(self, appdaemon_logger: AppdaemonLogger, config: SolarConfiguration) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.config = config

    def create_production_forecast(self, state: State) -> ProductionForecast:
        today = ProductionForecastDefault.create(state.pv_forecast_today)
        tomorrow = ProductionForecastDefault.create(state.pv_forecast_tomorrow)
        day_3 = ProductionForecastDefault.create(state.pv_forecast_day_3)

        return ProductionForecastComposite(today, tomorrow, day_3)

    def create_consumption_forecast(self, state: State) -> ConsumptionForecast:
        weather_forecast = self.create_weather_forecast(state)

        regular = ConsumptionForecastRegular(
            is_away_mode=state.is_away_mode or False,
            evening_start_hour=self.config.evening_start_hour,
            consumption_away=self.config.regular_consumption_away,
            consumption_day=self.config.regular_consumption_day,
            consumption_evening=self.config.regular_consumption_evening,
        )

        hvac_heating = ConsumptionForecastHvacHeating(
            forecast_weather=weather_forecast,
            is_eco_mode=state.is_eco_mode,
            hvac_heating_mode=state.hvac_heating_mode,
            t_in=state.indoor_temperature,
            cop_at_7c=self.config.heating_cop_at_7c,
            h=self.config.heating_h,
            temp_out_fallback=self.config.temp_out_fallback,
            humidity_out_fallback=self.config.humidity_out_fallback,
        )

        return ConsumptionForecastComposite(regular, hvac_heating)

    def create_price_forecast(self, state: State) -> PriceForecast:
        return PriceForecast.create(state.price_forecast_today)

    def create_weather_forecast(self, state: State) -> WeatherForecast:
        return WeatherForecast.create(state.weather_forecast)
