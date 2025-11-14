from datetime import datetime
from decimal import Decimal

import pytest
from solar.price_forecast import HourlyPrice, PriceForecast
from units.energy_price import EnergyPrice
from units.hourly_period import HourlyPeriod


def test_create_from_rce_15_mins() -> None:
    # RCE 15-min RCE forecast format
    raw_forecast = [
        {
            "dtime": "2025-10-03T13:00:00+00:00",
            "rce_pln": -10,  # capped to 0
        },
        {
            "dtime": "2025-10-03T13:15:00+00:00",
            "rce_pln": -10,  # capped to 0
        },
        {
            "dtime": "2025-10-03T13:30:00+00:00",
            "rce_pln": 50,
        },
        {
            "dtime": "2025-10-03T13:45:00+00:00",
            "rce_pln": 70,
        },
        {
            "dtime": "2025-10-03T14:00:00+00:00",
            "rce_pln": 100,
        },
        {
            "dtime": "2025-10-03T14:15:00+00:00",
            "rce_pln": 105,
        },
        {
            "dtime": "2025-10-03T14:30:00+00:00",
            "rce_pln": 105,
        },
        {
            "dtime": "2025-10-03T14:45:00+00:00",
            "rce_pln": 120,
        },
    ]

    forecast_price = PriceForecast.create_from_rce_15_mins(raw_forecast)

    assert forecast_price.periods == [
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T13:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("30")),
        ),
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T14:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("107.5")),
        ),
    ]


@pytest.fixture
def forecast_price() -> PriceForecast:
    return PriceForecast(
        [
            HourlyPrice(
                period=HourlyPeriod.parse("2025-10-03T16:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(426)),
            ),
            HourlyPrice(
                period=HourlyPeriod.parse("2025-10-03T17:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(538)),
            ),
            HourlyPrice(
                period=HourlyPeriod.parse("2025-10-03T18:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(538)),
            ),
            HourlyPrice(
                period=HourlyPeriod.parse("2025-10-03T19:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(825)),
            ),
        ]
    )


def test_find_peak_periods_for_4h(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_peak_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=4,
        price_threshold=EnergyPrice.pln_per_mwh(Decimal(500)),
    )

    assert results == [
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T17:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal(538)),
        ),
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T18:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal(538)),
        ),
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T19:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal(825)),
        ),
    ]


def test_find_peak_periods_for_3h(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_peak_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=3,
        price_threshold=EnergyPrice.pln_per_mwh(Decimal(500.0)),
    )

    assert results == [
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T17:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal(538)),
        ),
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T18:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal(538)),
        ),
    ]


def test_find_peak_periods_with_threshold_too_high(forecast_price: PriceForecast) -> None:
    results = forecast_price.find_peak_periods(
        period_start=datetime.fromisoformat("2025-10-03T15:00:00+00:00"),
        period_hours=4,
        price_threshold=EnergyPrice.pln_per_mwh(Decimal(1000)),
    )

    assert results == []


def test_find_daily_min_price_for_4h(forecast_price: PriceForecast) -> None:
    min_price = forecast_price.find_daily_min_price(datetime.fromisoformat("2025-10-03T15:00:00+00:00"), 4)

    assert min_price == EnergyPrice.pln_per_mwh(Decimal(426))


def test_find_daily_min_price_no_data(forecast_price: PriceForecast) -> None:
    min_price = forecast_price.find_daily_min_price(datetime.fromisoformat("2025-10-04T15:00:00+00:00"), 4)

    assert min_price is None
