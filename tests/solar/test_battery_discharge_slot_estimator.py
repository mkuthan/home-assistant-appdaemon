from dataclasses import replace
from datetime import datetime, time
from decimal import Decimal
from unittest.mock import Mock, call

import pytest
from solar.battery_discharge_slot import BatteryDischargeSlot
from solar.battery_discharge_slot_estimator import BatteryDischargeSlotEstimator
from solar.price_forecast import HourlyPrice
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice
from units.hourly_energy import HourlyConsumptionEnergy, HourlyProductionEnergy
from units.hourly_period import HourlyPeriod
from units.money import Money


@pytest.fixture
def battery_discharge_slot_estimator(
    configuration: SolarConfiguration,
    mock_appdaemon_logger: Mock,
    mock_forecast_factory: Mock,
) -> BatteryDischargeSlotEstimator:
    configuration = replace(
        configuration,
        battery_capacity=EnergyKwh(20.0),
        battery_voltage=BatteryVoltage(52.0),
        battery_maximum_current=BatteryCurrent(160.0),
        battery_reserve_soc_min=BatterySoc(20.0),
        battery_reserve_soc_margin=BatterySoc(5.0),
        battery_discharge_evening_margin=EnergyPrice.per_mwh(Money.pln(Decimal(650))),
        battery_discharge_morning_margin=EnergyPrice.per_mwh(Money.pln(Decimal(350))),
        battery_export_threshold_energy=EnergyKwh(1.0),
    )

    return BatteryDischargeSlotEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        configuration=configuration,
        forecast_factory=mock_forecast_factory,
    )


@pytest.mark.parametrize(
    ("battery_soc", "expected_start_time", "expected_end_time"),
    [
        (100.0, time(19, 27), time(21, 0)),
        (80.0, time(19, 56), time(21, 0)),
        (60.0, time(20, 0), time(20, 36)),
    ],
)
def test_estimate_battery_discharge_at_4_pm(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
    battery_soc: float,
    expected_start_time: time,
    expected_end_time: time,
) -> None:
    state = replace(state, battery_soc=BatterySoc(battery_soc))

    this_day = datetime.fromisoformat("2025-10-10T15:30:00+00:00")
    this_day_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    this_day_10_pm = datetime.fromisoformat("2025-10-10T22:00:00+00:00")
    high_tariff_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    daytime_hours = 9
    tomorrow_10_30_am = datetime.fromisoformat("2025-10-11T10:30:00+00:00")
    midday_hours = 4

    discharge_period = HourlyPeriod(this_day_4_pm)
    solar_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(2.0))],
        [HourlyProductionEnergy(solar_period, energy=EnergyKwh(20.0))],
    ]

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(4.0))],
        [HourlyConsumptionEnergy(solar_period, energy=EnergyKwh(1.0))],
    ]

    hourly_price_1 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T19:00:00+00:00"),
        price=EnergyPrice.per_mwh(Money.pln(Decimal(1250))),
    )
    hourly_price_2 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T20:00:00+00:00"),
        price=EnergyPrice.per_mwh(Money.pln(Decimal(1600))),
    )
    mock_price_forecast.hourly.return_value = [hourly_price_1, hourly_price_2]
    mock_price_forecast.average_price.return_value = EnergyPrice.per_mwh(Money.pln(Decimal(500)))

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(state, this_day)

    assert mock_production_forecast.hourly.call_args_list == [
        call(this_day_4_pm, high_tariff_hours),
        call(tomorrow_7_am, daytime_hours),
    ]
    assert mock_consumption_forecast.hourly.call_args_list == [
        call(this_day_4_pm, high_tariff_hours),
        call(tomorrow_7_am, daytime_hours),
    ]
    mock_price_forecast.hourly.assert_called_once_with(this_day_4_pm, this_day_10_pm)
    mock_price_forecast.average_price.assert_called_once_with(tomorrow_10_30_am, midday_hours)

    assert battery_discharge_slot == BatteryDischargeSlot(
        start_time=expected_start_time,
        end_time=expected_end_time,
        current=battery_discharge_slot_estimator.configuration.battery_maximum_current,
    )


def test_estimate_battery_discharge_at_4_pm_when_solar_cannot_replenish(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(100.0))

    this_day = datetime.fromisoformat("2025-10-10T13:30:00+00:00")
    this_day_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    high_tariff_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    daytime_hours = 9

    tomorrow_10_30_am = datetime.fromisoformat("2025-10-11T10:30:00+00:00")
    midday_hours = 4

    discharge_period = HourlyPeriod(this_day_4_pm)
    solar_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(2.0))],
        [HourlyProductionEnergy(solar_period, energy=EnergyKwh(5.0))],
    ]

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(4.0))],
        [HourlyConsumptionEnergy(solar_period, energy=EnergyKwh(1.0))],
    ]

    mock_price_forecast.average_price.return_value = EnergyPrice.per_mwh(Money.pln(Decimal(500)))

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(state, this_day)

    assert mock_production_forecast.hourly.call_args_list == [
        call(this_day_4_pm, high_tariff_hours),
        call(tomorrow_7_am, daytime_hours),
    ]
    assert mock_consumption_forecast.hourly.call_args_list == [
        call(this_day_4_pm, high_tariff_hours),
        call(tomorrow_7_am, daytime_hours),
    ]
    mock_price_forecast.hourly.assert_not_called()
    mock_price_forecast.average_price.assert_called_once_with(tomorrow_10_30_am, midday_hours)

    assert battery_discharge_slot is None


def test_estimate_battery_discharge_at_4_pm_when_surplus_energy_below_threshold(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(30.0))

    this_day = datetime.fromisoformat("2025-10-10T13:30:00+00:00")
    this_day_4_pm = datetime.fromisoformat("2025-10-10T16:00:00+00:00")
    high_tariff_hours = 6

    tomorrow_7_am = datetime.fromisoformat("2025-10-11T07:00:00+00:00")
    daytime_hours = 9
    tomorrow_10_30_am = datetime.fromisoformat("2025-10-11T10:30:00+00:00")
    midday_hours = 4

    discharge_period = HourlyPeriod(this_day_4_pm)
    solar_period = HourlyPeriod(tomorrow_7_am)

    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(2.0))],
        [HourlyProductionEnergy(solar_period, energy=EnergyKwh(20.0))],
    ]

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(4.0))],
        [HourlyConsumptionEnergy(solar_period, energy=EnergyKwh(1.0))],
    ]

    mock_price_forecast.average_price.return_value = EnergyPrice.per_mwh(Money.pln(Decimal(500)))

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(state, this_day)

    assert mock_production_forecast.hourly.call_args_list == [
        call(this_day_4_pm, high_tariff_hours),
        call(tomorrow_7_am, daytime_hours),
    ]
    assert mock_consumption_forecast.hourly.call_args_list == [
        call(this_day_4_pm, high_tariff_hours),
        call(tomorrow_7_am, daytime_hours),
    ]
    mock_price_forecast.hourly.assert_not_called()
    mock_price_forecast.average_price.assert_called_once_with(tomorrow_10_30_am, midday_hours)

    assert battery_discharge_slot is None


@pytest.mark.parametrize(
    ("battery_soc", "expected_start_time", "expected_end_time"),
    [
        (70.0, time(6, 56), time(8, 0)),
        (60.0, time(7, 0), time(7, 50)),
        (50.0, time(7, 0), time(7, 36)),
    ],
)
def test_estimate_battery_discharge_at_6_am(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
    battery_soc: float,
    expected_start_time: time,
    expected_end_time: time,
) -> None:
    state = replace(state, battery_soc=BatterySoc(battery_soc))

    this_day = datetime.fromisoformat("2025-10-10T05:30:00+00:00")
    this_day_6_am = datetime.fromisoformat("2025-10-10T06:00:00+00:00")
    this_day_7_am = datetime.fromisoformat("2025-10-10T07:00:00+00:00")
    this_day_9_am = datetime.fromisoformat("2025-10-10T09:00:00+00:00")
    high_tariff_hours = 6

    daytime_hours = 9
    today_10_30_am = datetime.fromisoformat("2025-10-10T10:30:00+00:00")
    midday_hours = 4

    discharge_period = HourlyPeriod(this_day_7_am)

    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(2.0))],
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(20.0))],
    ]

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(1.0))],
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(1.0))],
    ]

    hourly_price_0 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T06:00:00+00:00"),
        price=EnergyPrice.per_mwh(Money.pln(Decimal(800))),
    )
    hourly_price_1 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T07:00:00+00:00"),
        price=EnergyPrice.per_mwh(Money.pln(Decimal(950))),
    )
    hourly_price_2 = HourlyPrice(
        period=HourlyPeriod.parse("2025-10-10T08:00:00+00:00"),
        price=EnergyPrice.per_mwh(Money.pln(Decimal(750))),
    )
    mock_price_forecast.hourly.return_value = [hourly_price_0, hourly_price_1, hourly_price_2]
    mock_price_forecast.average_price.return_value = EnergyPrice.per_mwh(Money.pln(Decimal(100)))

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_6_am(state, this_day)

    assert mock_production_forecast.hourly.call_args_list == [
        call(this_day_7_am, high_tariff_hours),
        call(this_day_7_am, daytime_hours),
    ]
    assert mock_consumption_forecast.hourly.call_args_list == [
        call(this_day_7_am, high_tariff_hours),
        call(this_day_7_am, daytime_hours),
    ]
    mock_price_forecast.hourly.assert_called_once_with(this_day_6_am, this_day_9_am)
    mock_price_forecast.average_price.assert_called_once_with(today_10_30_am, midday_hours)

    assert battery_discharge_slot == BatteryDischargeSlot(
        start_time=expected_start_time,
        end_time=expected_end_time,
        current=battery_discharge_slot_estimator.configuration.battery_maximum_current,
    )


def test_estimate_battery_discharge_at_6_am_when_solar_cannot_replenish(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(70.0))

    this_day = datetime.fromisoformat("2025-10-10T05:30:00+00:00")
    this_day_7_am = datetime.fromisoformat("2025-10-10T07:00:00+00:00")
    high_tariff_hours = 6

    daytime_hours = 9
    today_10_30_am = datetime.fromisoformat("2025-10-10T10:30:00+00:00")
    midday_hours = 4

    discharge_period = HourlyPeriod(this_day_7_am)

    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(2.0))],
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(5.0))],
    ]

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(1.0))],
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(1.0))],
    ]

    mock_price_forecast.average_price.return_value = EnergyPrice.per_mwh(Money.pln(Decimal(800)))

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_6_am(state, this_day)

    assert mock_production_forecast.hourly.call_args_list == [
        call(this_day_7_am, high_tariff_hours),
        call(this_day_7_am, daytime_hours),
    ]
    assert mock_consumption_forecast.hourly.call_args_list == [
        call(this_day_7_am, high_tariff_hours),
        call(this_day_7_am, daytime_hours),
    ]
    mock_price_forecast.hourly.assert_not_called()
    mock_price_forecast.average_price.assert_called_once_with(today_10_30_am, midday_hours)

    assert battery_discharge_slot is None


def test_estimate_battery_discharge_at_6_am_when_surplus_energy_below_threshold(
    battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
    state: SolarState,
    mock_production_forecast: Mock,
    mock_consumption_forecast: Mock,
    mock_price_forecast: Mock,
) -> None:
    state = replace(state, battery_soc=BatterySoc(30.0))

    this_day = datetime.fromisoformat("2025-10-10T05:30:00+00:00")
    this_day_7_am = datetime.fromisoformat("2025-10-10T07:00:00+00:00")
    high_tariff_hours = 6

    daytime_hours = 9
    today_10_30_am = datetime.fromisoformat("2025-10-10T10:30:00+00:00")
    midday_hours = 4

    discharge_period = HourlyPeriod(this_day_7_am)

    mock_production_forecast.hourly.side_effect = [
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(2.0))],
        [HourlyProductionEnergy(discharge_period, energy=EnergyKwh(20.0))],
    ]

    mock_consumption_forecast.hourly.side_effect = [
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(4.0))],
        [HourlyConsumptionEnergy(discharge_period, energy=EnergyKwh(1.0))],
    ]

    mock_price_forecast.average_price.return_value = EnergyPrice.per_mwh(Money.pln(Decimal(100)))

    battery_discharge_slot = battery_discharge_slot_estimator.estimate_battery_discharge_at_6_am(state, this_day)

    assert mock_production_forecast.hourly.call_args_list == [
        call(this_day_7_am, high_tariff_hours),
        call(this_day_7_am, daytime_hours),
    ]
    assert mock_consumption_forecast.hourly.call_args_list == [
        call(this_day_7_am, high_tariff_hours),
        call(this_day_7_am, daytime_hours),
    ]
    mock_price_forecast.hourly.assert_not_called()
    mock_price_forecast.average_price.assert_called_once_with(today_10_30_am, midday_hours)

    assert battery_discharge_slot is None
