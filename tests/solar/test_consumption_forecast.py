from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from solar.consumption_forecast import (
    ConsumptionForecastComposite,
    ConsumptionForecastHvacHeating,
    ConsumptionForecastRegular,
)
from solar.weather_forecast import HourlyWeather
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy
from units.hourly_period import HourlyPeriod


@pytest.fixture
def any_datetime() -> datetime:
    return datetime.fromisoformat("2025-10-03T10:00:00+00:00")


@pytest.fixture
def any_hourly_period(any_datetime: datetime) -> HourlyPeriod:
    return HourlyPeriod(any_datetime)


class TestForecastConsumptionComposite:
    def test_hourly(self, any_datetime: datetime, any_hourly_period: HourlyPeriod) -> None:
        hourly1 = HourlyConsumptionEnergy(any_hourly_period, EnergyKwh(1.5))
        hourly2 = HourlyConsumptionEnergy(any_hourly_period, EnergyKwh(2.5))

        component_1 = Mock()
        component_1.hourly.return_value = [hourly1]

        component_2 = Mock()
        component_2.hourly.return_value = [hourly2]

        forecast = ConsumptionForecastComposite(component_1, component_2)

        result = forecast.hourly(period_start=any_datetime, period_hours=1)

        assert result == [hourly1, hourly2]


class TestForecastConsumptionRegular:
    @pytest.fixture
    def any_consumption_forecast_regular(self) -> ConsumptionForecastRegular:
        return ConsumptionForecastRegular(
            is_away_mode=False,
            evening_start_hour=16,
            consumption_away=EnergyKwh(0.5),
            consumption_day=EnergyKwh(0.6),
            consumption_evening=EnergyKwh(0.8),
        )

    def test_hourly_away_mode(
        self,
        any_consumption_forecast_regular: ConsumptionForecastRegular,
        any_datetime: datetime,
    ) -> None:
        forecast_consumption = any_consumption_forecast_regular
        forecast_consumption.is_away_mode = True

        result = forecast_consumption.hourly(period_start=any_datetime, period_hours=2)

        assert len(result) == 2
        assert result[0].period == HourlyPeriod(any_datetime)
        assert result[0].energy.value == pytest.approx(0.5)
        assert result[1].period == HourlyPeriod(any_datetime + timedelta(hours=1))
        assert result[1].energy.value == pytest.approx(0.5)

    def test_hourly_home_mode(self, any_consumption_forecast_regular: ConsumptionForecastRegular) -> None:
        forecast_consumption = any_consumption_forecast_regular
        forecast_consumption.is_away_mode = False

        period_start = datetime.fromisoformat("2025-10-03T15:00:00+00:00")

        result = forecast_consumption.hourly(period_start=period_start, period_hours=2)

        assert len(result) == 2
        assert result[0].period == HourlyPeriod(period_start)
        assert result[0].energy.value == pytest.approx(0.6)
        assert result[1].period == HourlyPeriod(period_start + timedelta(hours=1))
        assert result[1].energy.value == pytest.approx(0.8)


class TestForecastConsumptionHvacHeating:
    @pytest.fixture
    def mock_forecast_weather(self) -> Mock:
        return Mock()

    @pytest.fixture
    def mock_energy_estimator(self) -> Mock:
        return Mock()

    @pytest.fixture
    def any_consumption_forecast_hvac_heating(
        self, mock_forecast_weather: Mock, mock_energy_estimator: Mock
    ) -> ConsumptionForecastHvacHeating:
        return ConsumptionForecastHvacHeating(
            is_eco_mode=False,
            hvac_heating_mode="heat",
            t_in=20.0,
            cop_at_7c=3.5,
            h=0.18,
            forecast_weather=mock_forecast_weather,
            temp_out_fallback=5.0,
            humidity_out_fallback=75.0,
            energy_estimator=mock_energy_estimator,
        )

    def test_hourly_eco_mode(
        self,
        any_consumption_forecast_hvac_heating: ConsumptionForecastHvacHeating,
        mock_forecast_weather: Mock,
        any_datetime: datetime,
    ) -> None:
        forecast_consumption = any_consumption_forecast_hvac_heating
        forecast_consumption.is_eco_mode = True

        result = forecast_consumption.hourly(period_start=any_datetime, period_hours=2)

        assert len(result) == 2
        assert result[0].period == HourlyPeriod(any_datetime)
        assert result[0].energy.value == pytest.approx(0.0)
        assert result[1].period == HourlyPeriod(any_datetime + timedelta(hours=1))
        assert result[1].energy.value == pytest.approx(0.0)

        mock_forecast_weather.find_by_datetime.assert_not_called()

    def test_hourly_heating_mode_off(
        self,
        any_consumption_forecast_hvac_heating: ConsumptionForecastHvacHeating,
        mock_forecast_weather: Mock,
        any_datetime: datetime,
    ) -> None:
        forecast_consumption = any_consumption_forecast_hvac_heating
        forecast_consumption.hvac_heating_mode = "off"

        result = forecast_consumption.hourly(period_start=any_datetime, period_hours=2)

        assert len(result) == 2
        assert result[0].period == HourlyPeriod(any_datetime)
        assert result[0].energy.value == pytest.approx(0.0)
        assert result[1].period == HourlyPeriod(any_datetime + timedelta(hours=1))
        assert result[1].energy.value == pytest.approx(0.0)

        mock_forecast_weather.find_by_datetime.assert_not_called()

    def test_hourly_heating_mode_heat_with_weather_data(
        self,
        any_consumption_forecast_hvac_heating: ConsumptionForecastHvacHeating,
        mock_forecast_weather: Mock,
        mock_energy_estimator: Mock,
    ) -> None:
        forecast_consumption = any_consumption_forecast_hvac_heating
        forecast_consumption.is_eco_mode = False
        forecast_consumption.hvac_heating_mode = "heat"

        period_1 = datetime.fromisoformat("2025-10-03T10:00:00+00:00")
        period_2 = period_1 + timedelta(hours=1)
        period_3 = period_2 + timedelta(hours=1)

        mock_forecast_weather.find_by_datetime.side_effect = [
            HourlyWeather(
                period=HourlyPeriod(period_1),
                temperature=5.0,
                humidity=80.0,
            ),
            HourlyWeather(
                period=HourlyPeriod(period_2),
                temperature=3.0,
                humidity=75.0,
            ),
            HourlyWeather(
                period=HourlyPeriod(period_3),
                temperature=7.0,
                humidity=70.0,
            ),
        ]

        mock_energy_estimator.side_effect = [EnergyKwh(1.5), EnergyKwh(2.0), EnergyKwh(1.0)]

        result = forecast_consumption.hourly(period_start=period_1, period_hours=3)

        assert len(result) == 3
        assert result[0].period == HourlyPeriod(period_1)
        assert result[0].energy.value == pytest.approx(1.5)
        assert result[1].period == HourlyPeriod(period_2)
        assert result[1].energy.value == pytest.approx(2.0)
        assert result[2].period == HourlyPeriod(period_3)
        assert result[2].energy.value == pytest.approx(1.0)

        assert mock_forecast_weather.find_by_datetime.call_count == 3
        mock_forecast_weather.find_by_datetime.assert_any_call(period_1)
        mock_forecast_weather.find_by_datetime.assert_any_call(period_2)
        mock_forecast_weather.find_by_datetime.assert_any_call(period_3)

        assert mock_energy_estimator.call_count == 3
        mock_energy_estimator.assert_any_call(t_in=20.0, t_out=5.0, humidity=80.0, cop_at_7c=3.5, h=0.18)
        mock_energy_estimator.assert_any_call(t_in=20.0, t_out=3.0, humidity=75.0, cop_at_7c=3.5, h=0.18)
        mock_energy_estimator.assert_any_call(t_in=20.0, t_out=7.0, humidity=70.0, cop_at_7c=3.5, h=0.18)

    def test_total_heating_mode_heat_no_weather_data(
        self,
        any_consumption_forecast_hvac_heating: ConsumptionForecastHvacHeating,
        mock_forecast_weather: Mock,
        mock_energy_estimator: Mock,
    ) -> None:
        forecast_consumption = any_consumption_forecast_hvac_heating
        forecast_consumption.is_eco_mode = False
        forecast_consumption.hvac_heating_mode = "heat"

        period_1 = datetime.fromisoformat("2025-10-03T10:00:00+00:00")
        period_2 = period_1 + timedelta(hours=1)
        period_3 = period_2 + timedelta(hours=1)

        mock_forecast_weather.find_by_datetime.return_value = None

        mock_energy_estimator.side_effect = [EnergyKwh(1.5), EnergyKwh(2.0), EnergyKwh(1.0)]

        result = forecast_consumption.hourly(period_start=period_1, period_hours=3)

        assert len(result) == 3
        assert result[0].period == HourlyPeriod(period_1)
        assert result[0].energy.value == pytest.approx(1.5)
        assert result[1].period == HourlyPeriod(period_2)
        assert result[1].energy.value == pytest.approx(2.0)
        assert result[2].period == HourlyPeriod(period_3)
        assert result[2].energy.value == pytest.approx(1.0)

        assert mock_forecast_weather.find_by_datetime.call_count == 3
        mock_forecast_weather.find_by_datetime.assert_any_call(period_1)
        mock_forecast_weather.find_by_datetime.assert_any_call(period_2)
        mock_forecast_weather.find_by_datetime.assert_any_call(period_3)

        assert mock_energy_estimator.call_count == 3
        mock_energy_estimator.assert_any_call(t_in=20.0, t_out=5.0, humidity=75.0, cop_at_7c=3.5, h=0.18)
