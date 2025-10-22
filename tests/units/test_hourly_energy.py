import pytest
from units.energy_kwh import EnergyKwh
from units.hourly_energy import HourlyConsumptionEnergy, HourlyNetEnergy, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod


class TestHourlyEnergyStrMixin:
    @pytest.mark.parametrize(
        "energy_class",
        [
            HourlyConsumptionEnergy,
            HourlyProductionEnergy,
            HourlyNetEnergy,
        ],
    )
    def test_str(self, energy_class: type) -> None:
        energy = energy_class(HourlyPeriod.parse("2025-10-21T14:00:00+00:00"), EnergyKwh(50.5))
        assert f"{energy}" == "2025-10-21T14:00:00+00:00 50.50kWh"

    @pytest.mark.parametrize(
        "energy_class",
        [
            HourlyConsumptionEnergy,
            HourlyProductionEnergy,
            HourlyNetEnergy,
        ],
    )
    def test_format_list(self, energy_class: type) -> None:
        list = [
            energy_class(HourlyPeriod.parse("2025-10-21T14:00:00+00:00"), EnergyKwh(50.5)),
            energy_class(HourlyPeriod.parse("2025-10-21T15:00:00+00:00"), EnergyKwh(51.5)),
        ]

        expected = "[2025-10-21T14:00:00+00:00 50.50kWh, 2025-10-21T15:00:00+00:00 51.50kWh]"
        assert energy_class.format_list(list) == expected
