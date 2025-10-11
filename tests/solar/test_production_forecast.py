from datetime import datetime
from unittest.mock import Mock

import pytest
from solar.production_forecast import ProductionForecastComposite, ProductionForecastDefault, ProductionForecastPeriod
from units.energy_kwh import ENERGY_KWH_ZERO, EnergyKwh


class TestForecastProductionComposite:
    def test_estimate_energy_kwh(self) -> None:
        component_1 = Mock()
        component_1.estimate_energy_kwh.return_value = EnergyKwh(1.5)

        component_2 = Mock()
        component_2.estimate_energy_kwh.return_value = EnergyKwh(2.0)

        forecast_consumption = ProductionForecastComposite(component_1, component_2)
        period_start = datetime.fromisoformat("2025-10-03T10:00:00+00:00")

        result = forecast_consumption.estimate_energy_kwh(period_start=period_start, period_hours=3)

        # Total: 1.5 + 2.0 = 3.5 kWh
        assert result.value == pytest.approx(3.5)


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
            ProductionForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-02T06:00:00+00:00"),
                energy=EnergyKwh(1.0),
            ),
            ProductionForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-02T07:00:00+00:00"),
                energy=EnergyKwh(0.9),
            ),
        ]

    @pytest.fixture
    def forecast_periods(self) -> list[ProductionForecastPeriod]:
        return [
            ProductionForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-02T06:00:00+00:00"),
                energy=EnergyKwh(1.0),
            ),
            ProductionForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-02T07:00:00+00:00"),
                energy=EnergyKwh(2.0),
            ),
            ProductionForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-02T08:00:00+00:00"),
                energy=EnergyKwh(3.0),
            ),
            ProductionForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-02T09:00:00+00:00"),
                energy=EnergyKwh(4.0),
            ),
        ]

    def test_estimate_energy_kwh_exact_period_match(
        self,
        forecast_periods: list[ProductionForecastPeriod],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.estimate_energy_kwh(
            period_start=datetime.fromisoformat("2025-10-02T06:00:00+00:00"),
            period_hours=2,
        )

        assert result == EnergyKwh(3.0)  # 1.0 + 2.0

    def test_estimate_energy_kwh_partial_period_match(
        self,
        forecast_periods: list[ProductionForecastPeriod],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.estimate_energy_kwh(
            period_start=datetime.fromisoformat("2025-10-02T07:00:00+00:00"),
            period_hours=2,
        )

        assert result == EnergyKwh(5.0)  # 2.0 + 3.0

    def test_estimate_energy_kwh_all_periods(
        self,
        forecast_periods: list[ProductionForecastPeriod],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.estimate_energy_kwh(
            period_start=datetime.fromisoformat("2025-10-02T06:00:00+00:00"),
            period_hours=4,
        )

        assert result == EnergyKwh(10.0)  # 1.0 + 2.0 + 3.0 + 4.0

    def test_estimate_energy_kwh_no_matching_periods(
        self,
        forecast_periods: list[ProductionForecastPeriod],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.estimate_energy_kwh(
            period_start=datetime.fromisoformat("2025-10-02T10:00:00+00:00"),
            period_hours=2,
        )

        assert result == ENERGY_KWH_ZERO

    def test_estimate_energy_kwh_period_beyond_available_data(
        self,
        forecast_periods: list[ProductionForecastPeriod],
    ) -> None:
        forecast_production = ProductionForecastDefault(forecast_periods)

        result = forecast_production.estimate_energy_kwh(
            period_start=datetime.fromisoformat("2025-10-02T08:00:00+00:00"),
            period_hours=5,
        )

        assert result == EnergyKwh(7.0)  # 3.0 + 4.0
