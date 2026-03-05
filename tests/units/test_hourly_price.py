from decimal import Decimal

from units.energy_price import EnergyPrice
from units.hourly_period import HourlyPeriod
from units.hourly_price import HourlyPrice
from units.money import Money


def test_str() -> None:
    period = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-03T15:00:00+00:00"),
        price=EnergyPrice.per_mwh(Money.pln(Decimal(500))),
    )

    assert f"{period}" == "2025-10-03T15:00:00+00:00 500.00PLN/MWh"
