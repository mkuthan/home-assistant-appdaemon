from datetime import datetime
from decimal import Decimal

import pytest
from solar.price_forecast import PriceForecast
from units.energy_price import EnergyPrice
from units.fifteen_minute_period import FifteenMinutePeriod
from units.fifteen_minute_price import FifteenMinutePrice
from units.hourly_period import HourlyPeriod
from units.hourly_price import HourlyPrice


def test_create_from_rce_15_mins() -> None:
    raw_forecast = [
        {
            "dtime": "2025-10-03 13:00:00",
            "rce_pln": -10,
        },
        {
            "dtime": "2025-10-03 13:15:00",
            "rce_pln": 50,
        },
        {
            "dtime": "2025-10-03 13:30:00",
            "rce_pln": 50,
        },
        {
            "dtime": "2025-10-03 13:45:00",
            "rce_pln": 60,
        },
        {
            "dtime": "2025-10-03 14:00:00",
            "rce_pln": 60,
        },
        {
            "dtime": "2025-10-03 14:15:00",
            "rce_pln": 70,
        },
        {
            "dtime": "2025-10-03 14:30:00",
            "rce_pln": 70,
        },
        {
            "dtime": "2025-10-03 14:45:00",
            "rce_pln": 80,
        },
    ]

    forecast_price = PriceForecast.create_from_rce_15_mins(raw_forecast, "UTC")

    assert forecast_price.periods == [
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T13:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("-10")),
        ),
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T13:15:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("50")),
        ),
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T13:30:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("50")),
        ),
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T13:45:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("60")),
        ),
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T14:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("60")),
        ),
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T14:15:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("70")),
        ),
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T14:30:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("70")),
        ),
        FifteenMinutePrice(
            period=FifteenMinutePeriod.parse("2025-10-03T14:45:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("80")),
        ),
    ]

    assert forecast_price.hourly_periods == [
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T13:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("40.0")),  # -10 capped to 0
        ),
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T14:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal("70.0")),
        ),
    ]


@pytest.fixture
def forecast_price() -> PriceForecast:
    return PriceForecast(
        [
            # Hour 16:00 - prices 300, 400, 450, 480; avg 407.5
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T16:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(300)),
            ),
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T16:15:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(400)),
            ),
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T16:30:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(450)),
            ),
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T16:45:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(480)),
            ),
            # Hour 17:00 - prices 520, 600, 750, 800; avg 667.5
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T17:00:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(520)),
            ),
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T17:15:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(600)),
            ),
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T17:30:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(750)),
            ),
            FifteenMinutePrice(
                period=FifteenMinutePeriod.parse("2025-10-03T17:45:00+00:00"),
                price=EnergyPrice.pln_per_mwh(Decimal(800)),
            ),
        ]
    )


def test_find_min_hour(forecast_price: PriceForecast) -> None:
    min_hour = forecast_price.find_min_hour(
        period_start=datetime.fromisoformat("2025-10-03T16:00:00+00:00"),
        period_hours=2,
    )

    assert min_hour == HourlyPrice(
        period=HourlyPeriod.parse("2025-10-03T16:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(407.5)),
    )


def test_find_peak_hours(forecast_price: PriceForecast) -> None:
    peak_hours = forecast_price.find_peak_hours(
        period_start=datetime.fromisoformat("2025-10-03T16:00:00+00:00"),
        period_hours=2,
        price_threshold=EnergyPrice.pln_per_mwh(Decimal(500)),
    )

    assert peak_hours == [
        HourlyPrice(
            period=HourlyPeriod.parse("2025-10-03T17:00:00+00:00"),
            price=EnergyPrice.pln_per_mwh(Decimal(667.5)),
        ),
    ]
