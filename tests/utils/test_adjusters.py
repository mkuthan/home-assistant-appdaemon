from decimal import Decimal

import pytest
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice
from units.money import Money
from utils.adjusters import adjust_energy_surplus, adjust_export_threshold_price

PV_EXPORT_THRESHOLD_PRICE: int = 150
BATTERY_EXPORT_THRESHOLD_PRICE: int = 1200
INSTALLATION_CAPACITY = EnergyKwh(5.0)
GOOD_DAY_PRODUCTION = EnergyKwh(18.0)
BAD_DAY_PRODUCTION = EnergyKwh(10.0)


@pytest.mark.parametrize(
    "tomorrow_midday_average_price, expected_threshold",
    [
        # price below zero → non_negative clamps to 0 → full adjustment
        (-50, BATTERY_EXPORT_THRESHOLD_PRICE - PV_EXPORT_THRESHOLD_PRICE),
        # price at zero → non_negative = 0 → full adjustment
        (0, BATTERY_EXPORT_THRESHOLD_PRICE - PV_EXPORT_THRESHOLD_PRICE),
        # price below pv threshold → partial adjustment
        (100, BATTERY_EXPORT_THRESHOLD_PRICE - (PV_EXPORT_THRESHOLD_PRICE - 100)),
        # price equals pv threshold → zero adjustment
        (150, BATTERY_EXPORT_THRESHOLD_PRICE),
        # price above pv threshold → zero adjustment
        (200, BATTERY_EXPORT_THRESHOLD_PRICE),
    ],
)
def test_adjust_export_threshold_price_on_good_day(tomorrow_midday_average_price: int, expected_threshold: int) -> None:
    result = adjust_export_threshold_price(
        EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE))),
        EnergyPrice.per_mwh(Money.eur(Decimal(PV_EXPORT_THRESHOLD_PRICE))),
        EnergyPrice.per_mwh(Money.eur(Decimal(tomorrow_midday_average_price))),
        GOOD_DAY_PRODUCTION,
        INSTALLATION_CAPACITY,
    )

    assert result == EnergyPrice.per_mwh(Money.eur(Decimal(expected_threshold)))


def test_adjust_export_threshold_price_on_bad_day() -> None:
    result = adjust_export_threshold_price(
        EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE))),
        EnergyPrice.per_mwh(Money.eur(Decimal(PV_EXPORT_THRESHOLD_PRICE))),
        EnergyPrice.per_mwh(Money.eur(Decimal(50))),
        BAD_DAY_PRODUCTION,
        INSTALLATION_CAPACITY,
    )

    assert result == EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE)))


def test_adjust_export_threshold_price_when_midday_price_is_none() -> None:
    result = adjust_export_threshold_price(
        EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE))),
        EnergyPrice.per_mwh(Money.eur(Decimal(PV_EXPORT_THRESHOLD_PRICE))),
        None,
        GOOD_DAY_PRODUCTION,
        INSTALLATION_CAPACITY,
    )

    assert result == EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE)))


def test_adjust_energy_surplus_on_nominal_price() -> None:
    nominal_price = EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE)))
    adjusted_price = nominal_price

    energy_surplus = adjust_energy_surplus(
        EnergyKwh(10.0),
        nominal_price,
        adjusted_price,
    )

    assert energy_surplus == EnergyKwh(10.0)


def test_adjust_energy_surplus_on_lower_price() -> None:
    nominal_price = EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE)))
    adjusted_price = EnergyPrice.per_mwh(Money.eur(Decimal(BATTERY_EXPORT_THRESHOLD_PRICE - 100)))

    energy_surplus = adjust_energy_surplus(
        EnergyKwh(10.0),
        nominal_price,
        adjusted_price,
    )

    assert energy_surplus == EnergyKwh(5.0)
