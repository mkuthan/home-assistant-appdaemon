from datetime import datetime, time

import pytest
from solar.price_forecast import PriceForecast, PriceForecastPeriod
from units.energy_price import EnergyPrice


def test_create() -> None:
    # RCE forecast format
    raw_forecast = [
        {
            "hour": "2025-10-03T14:00:00+00:00",
            "price": 426.1,
        },
        {
            "hour": "2025-10-03T15:00:00+00:00",
            "price": 538.2,
        },
    ]

    forecast_price = PriceForecast.create(raw_forecast)

    assert forecast_price.periods == [
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T14:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(426.1),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
    ]


@pytest.fixture
def forecast_price() -> PriceForecast:
    return PriceForecast(
        [
            PriceForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-03T16:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(426.1),
            ),
            PriceForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-03T17:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(538.2),
            ),
            PriceForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-03T18:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(538.2),
            ),
            PriceForecastPeriod(
                datetime=datetime.fromisoformat("2025-10-03T19:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(825.1),
            ),
        ]
    )


def test_find_peak_periods_for_4h(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_peak_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=4,
        price_threshold=EnergyPrice.pln_per_mwh(500.0),
    )

    assert results == [
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T17:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T18:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T19:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(825.1),
        ),
    ]


def test_find_peak_periods_for_3h(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_peak_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=3,
        price_threshold=EnergyPrice.pln_per_mwh(500.0),
    )

    assert results == [
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T17:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T18:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
    ]


def test_find_peak_periods_with_threshold_too_high(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_peak_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=4,
        price_threshold=EnergyPrice.pln_per_mwh(1000.0),
    )

    assert results == []


def test_find_valley_period_for_4h(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_valley_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=4,
        price_threshold=EnergyPrice.pln_per_mwh(550.0),
    )

    assert results == [
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T16:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(426.1),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T17:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T18:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
    ]


def test_find_valley_period_for_3h(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_valley_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=3,
        price_threshold=EnergyPrice.pln_per_mwh(550.0),
    )

    assert results == [
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T16:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(426.1),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T17:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
        PriceForecastPeriod(
            datetime=datetime.fromisoformat("2025-10-03T18:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(538.2),
        ),
    ]


def test_find_valley_period_with_threshold_too_low(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_valley_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=4,
        price_threshold=EnergyPrice.pln_per_mwh(400.0),
    )

    assert results == []


def test_start_time_end_time() -> None:
    period = PriceForecastPeriod(
        datetime=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(500.0),
    )

    assert period.start_time() == time(15, 0)
    assert period.end_time() == time(16, 0)
