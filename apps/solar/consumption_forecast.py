from datetime import datetime, timedelta
from typing import Protocol

from solar.weather_forecast import WeatherForecast
from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh
from utils.hvac_estimators import estimate_heating_energy_consumption


class ConsumptionForecast(Protocol):
    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh: ...


class ConsumptionForecastComposite:
    def __init__(self, *components: ConsumptionForecast) -> None:
        self.components = components

    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        total_energy_kwh = ENERGY_KWH_ZERO
        for component in self.components:
            total_energy_kwh += component.estimate_energy_kwh(period_start, period_hours)
        return total_energy_kwh


class HeatingEnergyEstimator(Protocol):
    """Protocol for heating energy estimation function."""

    def __call__(
        self,
        t_out: float,
        t_in: float,
        humidity: float,
        cop_at_7c: float,
        h: float,
    ) -> EnergyKwh: ...


class ConsumptionForecastHvacHeating:
    def __init__(
        self,
        is_eco_mode: bool,
        hvac_heating_mode: str,
        t_in: float,
        cop_at_7c: float,
        h: float,
        forecast_weather: WeatherForecast,
        temp_out_fallback: float,
        humidity_out_fallback: float,
        energy_estimator: HeatingEnergyEstimator = estimate_heating_energy_consumption,
    ) -> None:
        self.is_eco_mode = is_eco_mode
        self.hvac_heating_mode = hvac_heating_mode
        self.t_in = t_in
        self.cop_at_7c = cop_at_7c
        self.h = h
        self.forecast_weather = forecast_weather
        self.temp_out_fallback = temp_out_fallback
        self.humidity_out_fallback = humidity_out_fallback

        self.energy_estimator = energy_estimator

    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        total_energy_kwh = ENERGY_KWH_ZERO

        if self.hvac_heating_mode == "heat" and not self.is_eco_mode:
            for hour_offset in range(period_hours):
                current = period_start + timedelta(hours=hour_offset)
                weather_period = self.forecast_weather.find_by_datetime(current)
                energy = self.energy_estimator(
                    t_in=self.t_in,
                    t_out=weather_period.temperature if weather_period else self.temp_out_fallback,
                    humidity=weather_period.humidity if weather_period else self.humidity_out_fallback,
                    cop_at_7c=self.cop_at_7c,
                    h=self.h,
                )
                total_energy_kwh += energy

        return total_energy_kwh


class ConsumptionForecastRegular:
    def __init__(
        self,
        is_away_mode: bool,
        evening_start_hour: int,
        consumption_away: EnergyKwh,
        consumption_day: EnergyKwh,
        consumption_evening: EnergyKwh,
    ) -> None:
        self.is_away_mode = is_away_mode
        self.evening_start_hour = evening_start_hour
        self.consumption_away = consumption_away
        self.consumption_day = consumption_day
        self.consumption_evening = consumption_evening

    def estimate_energy_kwh(self, period_start: datetime, period_hours: int) -> EnergyKwh:
        if self.is_away_mode:
            total_energy_kwh = self.consumption_away * period_hours
        else:
            total_energy_kwh = ENERGY_KWH_ZERO
            for hour_offset in range(period_hours):
                current = period_start + timedelta(hours=hour_offset)
                if current.hour >= self.evening_start_hour:
                    total_energy_kwh += self.consumption_evening
                else:
                    total_energy_kwh += self.consumption_day

        return total_energy_kwh
