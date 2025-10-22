from datetime import datetime
from unittest.mock import Mock

import pytest
from solar.production_forecast import HourlyProductionEnergy, ProductionForecastComposite, ProductionForecastDefault
from units.energy_kwh import EnergyKwh
from units.hourly_period import HourlyPeriod


@pytest.fixture
def any_datetime() -> datetime:
    return datetime.fromisoformat("2025-10-03T10:00:00+00:00")


@pytest.fixture
def any_hourly_period(any_datetime: datetime) -> HourlyPeriod:
    return HourlyPeriod(any_datetime)


class TestForecastProductionComposite:
    def test_hourly(self, any_datetime: datetime, any_hourly_period: HourlyPeriod) -> None:
        hourly1 = HourlyProductionEnergy(any_hourly_period, EnergyKwh(1.5))
        hourly2 = HourlyProductionEnergy(any_hourly_period, EnergyKwh(2.5))

        component_1 = Mock()
        component_1.hourly.return_value = [hourly1]

        component_2 = Mock()
        component_2.hourly.return_value = [hourly2]

        forecast = ProductionForecastComposite(component_1, component_2)

        result = forecast.hourly(period_start=any_datetime, period_hours=1)

        assert result == [hourly1, hourly2]


class TestForecastProductionDefault:
    def test_create(self) -> None:
        # Solcast forecast format
        raw_forecast = [
            {
                "period_start": "2025-10-02T06:00:00+00:00",
                "pv_estimate": 1.0,
            },
            {
                "period_start": "2025-10-02T07:00:00+00:00",
                "pv_estimate": 0.9,
            },
        ]

        forecast_production = ProductionForecastDefault.create(raw_forecast)

        assert forecast_production.periods == [
            HourlyProductionEnergy(
                period=HourlyPeriod.parse("2025-10-02T06:00:00+00:00"),
                energy=EnergyKwh(1.0),
            ),
            HourlyProductionEnergy(
                period=HourlyPeriod.parse("2025-10-02T07:00:00+00:00"),
                energy=EnergyKwh(0.9),
            ),
        ]

    @pytest.fixture
    def forecast_periods(self) -> list[HourlyProductionEnergy]:
        return [
            HourlyProductionEnergy(
                period=HourlyPeriod.parse("2025-10-02T06:00:00+00:00"),
                energy=EnergyKwh(1.0),
            ),
            HourlyProductionEnergy(
                period=HourlyPeriod.parse("2025-10-02T07:00:00+00:00"),
                energy=EnergyKwh(2.0),
            ),
            HourlyProductionEnergy(
                period=HourlyPeriod.parse("2025-10-02T08:00:00+00:00"),
                energy=EnergyKwh(3.0),
            ),
            HourlyProductionEnergy(
                period=HourlyPeriod.parse("2025-10-02T09:00:00+00:00"),
                energy=EnergyKwh(4.0),
            ),
        ]

    def test_hourly_2_periods(
        self,
        forecast_periods: list[HourlyProductionEnergy],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.hourly(
            period_start=datetime.fromisoformat("2025-10-02T07:00:00+00:00"),
            period_hours=2,
        )

        assert result == forecast_periods[1:3]

    def test_hourly_all_periods(
        self,
        forecast_periods: list[HourlyProductionEnergy],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.hourly(
            period_start=datetime.fromisoformat("2025-10-02T06:00:00+00:00"),
            period_hours=4,
        )

        assert result == forecast_periods

    def test_hourly_beyond_periods(
        self,
        forecast_periods: list[HourlyProductionEnergy],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.hourly(
            period_start=datetime.fromisoformat("2025-10-02T08:00:00+00:00"),
            period_hours=5,
        )

        assert result == forecast_periods[2:4]

    def test_hourly_no_matching_periods(
        self,
        forecast_periods: list[HourlyProductionEnergy],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.hourly(
            period_start=datetime.fromisoformat("2025-10-02T10:00:00+00:00"),
            period_hours=2,
        )

        assert result == []
