from datetime import datetime, timedelta
from typing import Protocol

from entities.entities import is_heating_enabled
from solar.weather_forecast import WeatherForecast
from units.celsius import Celsius
from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy
from units.hourly_period import HourlyPeriod
from units.hourly_weather import HourlyWeather
from utils.hvac_estimators import estimate_heating_energy_consumption, estimate_heating_idle_until
from utils.time_utils import truncate_to_hour


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


class HeatingIdleEstimator(Protocol):
    def __call__(
        self,
        now: datetime,
        t_in_actual: Celsius,
        t_in_target: Celsius,
        hourly_weather: list[HourlyWeather],
        decay_rate: float,
    ) -> datetime: ...


# Heating energy consumption forecast, assumes steady heat pump operation regardless of eco mode,
# except while indoor temperature above the target decays.
class ConsumptionForecastHvacHeating:
    _IDLE_HORIZON_HOURS = 24

    def __init__(
        self,
        now: datetime,
        hvac_heating_mode: str,
        t_in: Celsius,
        t_in_actual: Celsius,
        t_in_target: Celsius,
        cop_at_7c: float,
        h: float,
        decay_rate: float,
        forecast_weather: WeatherForecast,
        temp_out_fallback: Celsius,
        humidity_out_fallback: float,
        energy_estimator: HeatingEnergyEstimator = estimate_heating_energy_consumption,
        idle_estimator: HeatingIdleEstimator = estimate_heating_idle_until,
    ) -> None:
        self.now = now
        self.hvac_heating_mode = hvac_heating_mode
        self.t_in = t_in
        self.t_in_actual = t_in_actual
        self.t_in_target = t_in_target
        self.cop_at_7c = cop_at_7c
        self.h = h
        self.decay_rate = decay_rate
        self.forecast_weather = forecast_weather
        self.temp_out_fallback = temp_out_fallback
        self.humidity_out_fallback = humidity_out_fallback

        self.energy_estimator = energy_estimator
        self.idle_estimator = idle_estimator

    def hourly(self, period_start: datetime, period_hours: int) -> list[HourlyConsumptionEnergy]:
        if not is_heating_enabled(self.hvac_heating_mode):
            return [
                HourlyConsumptionEnergy(
                    period=HourlyPeriod(period_start + timedelta(hours=hour_offset)),
                    energy=ENERGY_KWH_ZERO,
                )
                for hour_offset in range(period_hours)
            ]

        heating_idle_until = self.idle_estimator(
            now=self.now,
            t_in_actual=self.t_in_actual,
            t_in_target=self.t_in_target,
            hourly_weather=self._hourly_weather(truncate_to_hour(self.now), self._IDLE_HORIZON_HOURS),
            decay_rate=self.decay_rate,
        )

        periods = []
        for weather in self._hourly_weather(period_start, period_hours):
            if heating_idle_until >= weather.period.end:
                energy = ENERGY_KWH_ZERO
            else:
                energy = self.energy_estimator(
                    t_in=self.t_in,
                    t_out=weather.temperature,
                    humidity=weather.humidity,
                    cop_at_7c=self.cop_at_7c,
                    h=self.h,
                )

            periods.append(
                HourlyConsumptionEnergy(
                    period=weather.period,
                    energy=energy,
                )
            )
        return periods

    def _hourly_weather(self, period_start: datetime, period_hours: int) -> list[HourlyWeather]:
        return self.forecast_weather.hourly(
            period_start, period_hours, self.temp_out_fallback, self.humidity_out_fallback
        )


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
