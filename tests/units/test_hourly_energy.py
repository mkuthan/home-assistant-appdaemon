import pytest
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


class TestHourlyEnergyStrMixin:
    @pytest.mark.parametrize(
        "energy_class",
        [
            HourlyConsumptionEnergy,
            HourlyProductionEnergy,
        ],
    )
    def test_str(self, energy_class: type) -> None:
        energy = energy_class(HourlyPeriod.parse("2025-10-21T14:00:00+00:00"), EnergyKwh(50.5))
        assert f"{energy}" == "2025-10-21T14:00:00+00:00 50.50kWh"
