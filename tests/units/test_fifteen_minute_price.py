from decimal import Decimal

from units.energy_price import EnergyPrice
from units.fifteen_minute_period import FifteenMinutePeriod
from units.fifteen_minute_price import FifteenMinutePrice


def test_str() -> None:
    period = FifteenMinutePrice(
        period=FifteenMinutePeriod.parse("2025-10-03T15:15:00+00:00"),
        price=EnergyPrice.pln_per_mwh(Decimal(500)),
    )

    assert f"{period}" == "2025-10-03T15:15:00+00:00 500.00PLN/MWh"
