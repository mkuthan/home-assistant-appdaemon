from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from solar.consumption_forecast import (
    ConsumptionForecastComposite,
    ConsumptionForecastHvacHeating,
    ConsumptionForecastRegular,
)
from solar.weather_forecast import HourlyWeather
from units.celsius import Celsius
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
    def mock_idle_estimator(self) -> Mock:
        return Mock()

    @pytest.fixture
    def any_consumption_forecast_hvac_heating(
        self,
        any_datetime: datetime,
        mock_forecast_weather: Mock,
        mock_sensor_publisher: Mock,
        mock_energy_estimator: Mock,
        mock_idle_estimator: Mock,
    ) -> ConsumptionForecastHvacHeating:
        return ConsumptionForecastHvacHeating(
            now=any_datetime,
            hvac_heating_mode="heat",
            t_in=Celsius(20.0),
            t_in_actual=Celsius(21.0),
            t_in_target=Celsius(19.0),
            cop_at_7c=3.5,
            h=0.18,
            decay_rate=0.02,
            forecast_weather=mock_forecast_weather,
            temp_out_fallback=Celsius(5.0),
            humidity_out_fallback=75.0,
            sensor_publisher=mock_sensor_publisher,
            energy_estimator=mock_energy_estimator,
            idle_estimator=mock_idle_estimator,
        )

    @pytest.fixture
    def any_hourly_weather(self) -> list[HourlyWeather]:
        return [
            HourlyWeather(
                period=HourlyPeriod.parse("2025-10-03T10:00:00+00:00"),
                temperature=Celsius(5.0),
                humidity=80.0,
            ),
            HourlyWeather(
                period=HourlyPeriod.parse("2025-10-03T11:00:00+00:00"),
                temperature=Celsius(3.0),
                humidity=75.0,
            ),
            HourlyWeather(
                period=HourlyPeriod.parse("2025-10-03T12:00:00+00:00"),
                temperature=Celsius(7.0),
                humidity=70.0,
            ),
        ]

    def test_hourly_heating_mode_off(
        self,
        any_consumption_forecast_hvac_heating: ConsumptionForecastHvacHeating,
        mock_sensor_publisher: Mock,
        mock_idle_estimator: Mock,
        mock_energy_estimator: Mock,
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

        mock_sensor_publisher.publish.assert_not_called()
        mock_idle_estimator.assert_not_called()
        mock_energy_estimator.assert_not_called()

    def test_hourly_heating_mode_heat(
        self,
        any_consumption_forecast_hvac_heating: ConsumptionForecastHvacHeating,
        any_hourly_weather: list[HourlyWeather],
        mock_forecast_weather: Mock,
        mock_sensor_publisher: Mock,
        mock_idle_estimator: Mock,
        mock_energy_estimator: Mock,
        any_datetime: datetime,
    ) -> None:
        forecast_consumption = any_consumption_forecast_hvac_heating

        period_1 = datetime.fromisoformat("2025-10-03T10:00:00+00:00")
        period_2 = period_1 + timedelta(hours=1)
        period_3 = period_2 + timedelta(hours=1)

        mock_forecast_weather.hourly.return_value = any_hourly_weather
        mock_idle_estimator.return_value = any_datetime
        mock_energy_estimator.side_effect = [EnergyKwh(1.5), EnergyKwh(2.0), EnergyKwh(1.0)]

        result = forecast_consumption.hourly(period_start=period_1, period_hours=3)

        assert len(result) == 3
        assert result[0].period == HourlyPeriod(period_1)
        assert result[0].energy.value == pytest.approx(1.5)
        assert result[1].period == HourlyPeriod(period_2)
        assert result[1].energy.value == pytest.approx(2.0)
        assert result[2].period == HourlyPeriod(period_3)
        assert result[2].energy.value == pytest.approx(1.0)

        mock_forecast_weather.hourly.assert_any_call(any_datetime, 24, Celsius(5.0), 75.0)
        mock_forecast_weather.hourly.assert_any_call(period_1, 3, Celsius(5.0), 75.0)

        mock_idle_estimator.assert_called_once_with(
            now=any_datetime,
            t_in_actual=Celsius(21.0),
            t_in_target=Celsius(19.0),
            hourly_weather=any_hourly_weather,
            decay_rate=0.02,
        )

        mock_sensor_publisher.publish.assert_called_once_with(
            "heating_idle_until",
            "2025-10-03T10:00:00+00:00",
            {
                "device_class": "timestamp",
                "hvac_heating_mode": "heat",
                "t_in_actual": Celsius(21.0),
                "t_in_target": Celsius(19.0),
                "excess": Celsius(2.0),
                "decay_rate": 0.02,
                "idle_hours": 0.0,
                "t_out_avg": 5.0,
                "t_out_min": 3.0,
                "estimated_at": any_datetime,
            },
        )

        assert mock_energy_estimator.call_count == 3
        mock_energy_estimator.assert_any_call(
            t_in=Celsius(20.0), t_out=Celsius(5.0), humidity=80.0, cop_at_7c=3.5, h=0.18
        )
        mock_energy_estimator.assert_any_call(
            t_in=Celsius(20.0), t_out=Celsius(3.0), humidity=75.0, cop_at_7c=3.5, h=0.18
        )
        mock_energy_estimator.assert_any_call(
            t_in=Celsius(20.0), t_out=Celsius(7.0), humidity=70.0, cop_at_7c=3.5, h=0.18
        )

    @pytest.mark.parametrize(
        "heating_idle_until",
        [
            # Idle period covers the first hour
            "2025-10-03T11:00:00+00:00",
            # Idle period partially covers the second hour
            "2025-10-03T11:30:00+00:00",
        ],
    )
    def test_hourly_heating_mode_heat_idle(
        self,
        any_consumption_forecast_hvac_heating: ConsumptionForecastHvacHeating,
        any_hourly_weather: list[HourlyWeather],
        mock_forecast_weather: Mock,
        mock_idle_estimator: Mock,
        mock_energy_estimator: Mock,
        heating_idle_until: str,
    ) -> None:
        forecast_consumption = any_consumption_forecast_hvac_heating

        period_1 = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        mock_forecast_weather.hourly.return_value = any_hourly_weather
        mock_idle_estimator.return_value = datetime.fromisoformat(heating_idle_until)
        mock_energy_estimator.side_effect = [EnergyKwh(2.0), EnergyKwh(1.0)]

        result = forecast_consumption.hourly(period_start=period_1, period_hours=3)

        assert len(result) == 3
        assert result[0].energy.value == pytest.approx(0.0)
        assert result[1].energy.value == pytest.approx(2.0)
        assert result[2].energy.value == pytest.approx(1.0)

        assert mock_energy_estimator.call_count == 2
