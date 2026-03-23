from decimal import Decimal

import pytest
from units.energy_price import EnergyPrice
from units.money import Money
from utils.price_estimators import adjust_export_threshold_price

PV_EXPORT_THRESHOLD_PRICE: int = 150


@pytest.mark.parametrize(
    "tomorrow_midday_average_price, expected_threshold",
    [
        # price below zero → non_negative clamps to 0 → full adjustment
        (-50, PV_EXPORT_THRESHOLD_PRICE),
        # price at zero → non_negative = 0 → full adjustment
        (0, PV_EXPORT_THRESHOLD_PRICE),
        # price below pv threshold → partial adjustment
        (100, PV_EXPORT_THRESHOLD_PRICE - 100),
        # price equals pv threshold → zero adjustment
        (150, 0),
        # price above pv threshold → zero adjustment
        (200, 0),
    ],
)
def test_adjust_export_threshold_price(tomorrow_midday_average_price: int, expected_threshold: int) -> None:
    result = adjust_export_threshold_price(
        EnergyPrice.per_mwh(Money.eur(Decimal(PV_EXPORT_THRESHOLD_PRICE))),
        EnergyPrice.per_mwh(Money.eur(Decimal(tomorrow_midday_average_price))),
    )

    assert result == EnergyPrice.per_mwh(Money.eur(Decimal(expected_threshold)))
