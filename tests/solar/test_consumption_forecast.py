from datetime import datetime
from unittest.mock import Mock

import pytest
from solar.consumption_forecast import (
    ConsumptionForecastComposite,
    ConsumptionForecastHvacHeating,
    ConsumptionForecastRegular,
)
from solar.weather_forecast import HourlyWeather
from units.energy_kwh import EnergyKwh
from units.hourly_period import HourlyPeriod


class TestForecastConsumptionComposite:
    def test_total(self, mock_appdaemon_logger: Mock) -> None:
        component_1 = Mock()
        component_1.total.return_value = EnergyKwh(1.5)

        component_2 = Mock()
        component_2.total.return_value = EnergyKwh(2.0)

        forecast_consumption = ConsumptionForecastComposite(mock_appdaemon_logger, component_1, component_2)
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=3)

        # Total: 1.5 + 2.0 = 3.5 kWh
        assert result.value == pytest.approx(3.5)


class TestForecastConsumptionRegular:
    def test_total_away_mode(self) -> None:
        forecast_consumption = ConsumptionForecastRegular(
            is_away_mode=True,
            evening_start_hour=16,
            consumption_away=EnergyKwh(0.5),
            consumption_day=EnergyKwh(0.6),
            consumption_evening=EnergyKwh(0.8),
        )
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=4)

        # 0.5 * 4 hours = 2.0 kWh
        assert result.value == pytest.approx(2.0)

    def test_total_home_mode_daytime_only(self) -> None:
        forecast_consumption = ConsumptionForecastRegular(
            is_away_mode=False,
            evening_start_hour=16,
            consumption_away=EnergyKwh(0.5),
            consumption_day=EnergyKwh(0.6),
            consumption_evening=EnergyKwh(0.8),
        )
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=3)

        # 0.6 * 3 hours = 1.8 kWh
        assert result.value == pytest.approx(1.8)

    def test_total_home_mode_evening_only(self) -> None:
        forecast_consumption = ConsumptionForecastRegular(
            is_away_mode=False,
            evening_start_hour=16,
            consumption_away=EnergyKwh(0.5),
            consumption_day=EnergyKwh(0.6),
            consumption_evening=EnergyKwh(0.8),
        )
        period_start = datetime.fromisoformat("2025-10-03T18:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=3)

        # 0.8 * 3 hours = 2.4 kWh
        assert result.value == pytest.approx(2.4)

    def test_total_home_mode_crossing_evening_boundary(self) -> None:
        forecast_consumption = ConsumptionForecastRegular(
            is_away_mode=False,
            evening_start_hour=16,
            consumption_away=EnergyKwh(0.5),
            consumption_day=EnergyKwh(0.6),
            consumption_evening=EnergyKwh(0.8),
        )
        period_start = datetime.fromisoformat("2025-10-03T14:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=4)

        # 2 * 0.6 + 2 * 0.8 = 2.8 kWh
        assert result.value == pytest.approx(2.8)


class TestForecastConsumptionHvacHeating:
    @pytest.fixture
    def mock_forecast_weather(self) -> Mock:
        return Mock()

    def test_total_eco_mode(self, mock_forecast_weather: Mock) -> None:
        forecast_consumption = ConsumptionForecastHvacHeating(
            is_eco_mode=True,
            hvac_heating_mode="heat",
            t_in=20.0,
            cop_at_7c=3.5,
            h=0.18,
            forecast_weather=mock_forecast_weather,
            temp_out_fallback=5.0,
            humidity_out_fallback=75.0,
        )
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=3)

        # Eco mode: no heating regardless of mode
        assert result.value == pytest.approx(0.0)
        mock_forecast_weather.find_by_datetime.assert_not_called()

    def test_total_heating_mode_off(self, mock_forecast_weather: Mock) -> None:
        forecast_consumption = ConsumptionForecastHvacHeating(
            is_eco_mode=False,
            hvac_heating_mode="off",
            t_in=20.0,
            cop_at_7c=3.5,
            h=0.18,
            forecast_weather=mock_forecast_weather,
            temp_out_fallback=5.0,
            humidity_out_fallback=75.0,
        )
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=3)

        # Heating mode off: no heating
        assert result.value == pytest.approx(0.0)
        mock_forecast_weather.find_by_datetime.assert_not_called()

    def test_total_heating_mode_heat_with_weather_data(self, mock_forecast_weather: Mock) -> None:
        period_1 = HourlyWeather(
            period=HourlyPeriod.parse("2025-10-03T10:00:00+00:00"),
            temperature=5.0,
            humidity=80.0,
        )
        period_2 = HourlyWeather(
            period=HourlyPeriod.parse("2025-10-03T11:00:00+00:00"),
            temperature=3.0,
            humidity=75.0,
        )
        period_3 = HourlyWeather(
            period=HourlyPeriod.parse("2025-10-03T12:00:00+00:00"),
            temperature=7.0,
            humidity=70.0,
        )

        mock_forecast_weather.find_by_datetime.side_effect = [period_1, period_2, period_3]

        mock_estimate = Mock(side_effect=[EnergyKwh(1.5), EnergyKwh(2.0), EnergyKwh(1.0)])

        forecast_consumption = ConsumptionForecastHvacHeating(
            is_eco_mode=False,
            hvac_heating_mode="heat",
            t_in=20.0,
            cop_at_7c=3.5,
            h=0.18,
            forecast_weather=mock_forecast_weather,
            temp_out_fallback=5.0,
            humidity_out_fallback=75.0,
            energy_estimator=mock_estimate,
        )
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=3)

        # Total: 1.5 + 2.0 + 1.0 = 4.5 kWh
        assert result.value == pytest.approx(4.5)

        assert mock_forecast_weather.find_by_datetime.call_count == 3
        mock_forecast_weather.find_by_datetime.assert_any_call(datetime.fromisoformat("2025-10-03T10:00:00+00:00"))
        mock_forecast_weather.find_by_datetime.assert_any_call(datetime.fromisoformat("2025-10-03T11:00:00+00:00"))
        mock_forecast_weather.find_by_datetime.assert_any_call(datetime.fromisoformat("2025-10-03T12:00:00+00:00"))

        assert mock_estimate.call_count == 3
        mock_estimate.assert_any_call(t_in=20.0, t_out=5.0, humidity=80.0, cop_at_7c=3.5, h=0.18)
        mock_estimate.assert_any_call(t_in=20.0, t_out=3.0, humidity=75.0, cop_at_7c=3.5, h=0.18)
        mock_estimate.assert_any_call(t_in=20.0, t_out=7.0, humidity=70.0, cop_at_7c=3.5, h=0.18)

    def test_total_heating_mode_heat_no_weather_data(self, mock_forecast_weather: Mock) -> None:
        mock_forecast_weather.find_by_datetime.return_value = None

        mock_estimate = Mock(side_effect=[EnergyKwh(1.2), EnergyKwh(1.2)])

        forecast_consumption = ConsumptionForecastHvacHeating(
            is_eco_mode=False,
            hvac_heating_mode="heat",
            t_in=20.0,
            cop_at_7c=3.5,
            h=0.18,
            forecast_weather=mock_forecast_weather,
            temp_out_fallback=5.0,
            humidity_out_fallback=80.0,
            energy_estimator=mock_estimate,
        )
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.total(period_start=period_start, period_hours=2)

        # Total: 1.2 + 1.2 = 2.4 kWh
        assert result.value == pytest.approx(2.4)

        assert mock_forecast_weather.find_by_datetime.call_count == 2

        assert mock_estimate.call_count == 2
        mock_estimate.assert_any_call(
            t_in=20.0,
            t_out=5.0,
            humidity=80.0,
            cop_at_7c=3.5,
            h=0.18,
        )
