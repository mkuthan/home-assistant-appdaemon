from datetime import datetime, timedelta
from typing import Protocol

from entities.entities import is_heating_enabled
from solar.weather_forecast import WeatherForecast
from units.celsius import Celsius
from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy
from units.hourly_period import HourlyPeriod
from utils.hvac_estimators import estimate_heating_energy_consumption


class ConsumptionForecast(Protocol):
    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyConsumptionEnergy]: ...


class ConsumptionForecastComposite:
    def __init__(self, *components: ConsumptionForecast) -> None:
        self.components = components

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyConsumptionEnergy]:
        return [item for component in self.components for item in component.hourly(period_start, period_hours)]


class HeatingEnergyEstimator(Protocol):
    def __call__(
        self,
        t_out: Celsius,
        t_in: Celsius,
        humidity: float,
        cop_at_7c: float,
        h: float,
    ) -> EnergyKwh: ...


# Heating energy consumption forecast excluding energy consumption
# during low-tariff periods (outside forecasted hours)
class ConsumptionForecastHvacHeating:
    def __init__(
        self,
        indoor_temperature: Celsius,
        hvac_heating_mode: str,
        hvac_heating_temperature: Celsius,
        t_in: Celsius,
        cop_at_7c: float,
        h: float,
        forecast_weather: WeatherForecast,
        temp_out_fallback: Celsius,
        humidity_out_fallback: float,
        energy_estimator: HeatingEnergyEstimator = estimate_heating_energy_consumption,
    ) -> None:
        self.indoor_temperature = indoor_temperature
        self.hvac_heating_mode = hvac_heating_mode
        self.hvac_heating_temperature = hvac_heating_temperature
        self.t_in = t_in
        self.cop_at_7c = cop_at_7c
        self.h = h
        self.forecast_weather = forecast_weather
        self.temp_out_fallback = temp_out_fallback
        self.humidity_out_fallback = humidity_out_fallback

        self.energy_estimator = energy_estimator

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyConsumptionEnergy]:
        periods = []

        is_overheated = self.indoor_temperature > self.hvac_heating_temperature

        for hour_offset in range(period_hours):
            current = period_start + timedelta(hours=hour_offset)

            if is_heating_enabled(self.hvac_heating_mode) and not is_overheated:
                weather_period = self.forecast_weather.find_by_datetime(current)
                energy = self.energy_estimator(
                    t_in=self.t_in,
                    t_out=weather_period.temperature if weather_period else self.temp_out_fallback,
                    humidity=weather_period.humidity if weather_period else self.humidity_out_fallback,
                    cop_at_7c=self.cop_at_7c,
                    h=self.h,
                )
            else:
                energy = ENERGY_KWH_ZERO

            periods.append(
                HourlyConsumptionEnergy(
                    period=HourlyPeriod(current),
                    energy=energy,
                )
            )
        return periods


# Lights, appliances, etc. consumption forecast using simple time-of-day model.
class ConsumptionForecastRegular:
    EVENING_START_HOUR = 16

    def __init__(
        self,
        is_away_mode: bool,
        consumption_away: EnergyKwh,
        consumption_day: EnergyKwh,
        consumption_evening: EnergyKwh,
    ) -> None:
        self.is_away_mode = is_away_mode
        self.consumption_away = consumption_away
        self.consumption_day = consumption_day
        self.consumption_evening = consumption_evening

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyConsumptionEnergy]:
        periods = []
        for hour_offset in range(period_hours):
            current = period_start + timedelta(hours=hour_offset)

            if self.is_away_mode:
                energy = self.consumption_away
            else:
                if current.hour >= self.EVENING_START_HOUR:
                    energy = self.consumption_evening
                else:
                    energy = self.consumption_day

            periods.append(
                HourlyConsumptionEnergy(
                    period=HourlyPeriod(current),
                    energy=energy,
                )
            )
        return periods
