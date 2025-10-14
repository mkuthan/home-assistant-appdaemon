from dataclasses import replace
from datetime import datetime, time
from unittest.mock import Mock

from solar.battery_discharge_slot_estimator import BatteryDischargeSlotEstimator
from solar.price_forecast import PriceForecast, PriceForecastPeriod
from solar.solar_configuration import SolarConfiguration
from solar.state import State
from units.battery_current import BatteryCurrent
from units.battery_discharge_slot import BatteryDischargeSlot
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice


def test_call_returns_discharge_slot_when_surplus_energy_and_peak_price(
    mock_appdaemon_logger: Mock,
    config: SolarConfiguration,
    state: State,
) -> None:
    config = replace(
        config,
        battery_capacity=EnergyKwh(10.0),
        battery_voltage=BatteryVoltage(50.0),
        battery_maximum_current=BatteryCurrent(80.0),
        battery_reserve_soc_min=BatterySoc(20.0),
        battery_reserve_soc_margin=BatterySoc(5.0),
        battery_export_threshold_price=EnergyPrice.pln_per_mwh(1200.0),
        battery_export_threshold_energy=EnergyKwh(1.0),
    )

    state = replace(state, battery_soc=BatterySoc(100.0))

    mock_production_forecast = Mock()
    mock_production_forecast.estimate_energy_kwh.return_value = EnergyKwh(2.0)

    mock_consumption_forecast = Mock()
    mock_consumption_forecast.estimate_energy_kwh.return_value = EnergyKwh(4.0)

    peak_period_1 = PriceForecastPeriod(
        datetime=datetime.fromisoformat("2025-10-10T19:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(1250.0),
    )
    peak_period_2 = PriceForecastPeriod(
        datetime=datetime.fromisoformat("2025-10-10T20:00:00+00:00"),
        price=EnergyPrice.pln_per_mwh(1600.0),
    )
    mock_price_forecast = Mock(spec=PriceForecast)
    mock_price_forecast.find_peak_periods.return_value = [peak_period_1, peak_period_2]

    mock_forecast_factory = Mock()
    mock_forecast_factory.create_production_forecast.return_value = mock_production_forecast
    mock_forecast_factory.create_consumption_forecast.return_value = mock_consumption_forecast
    mock_forecast_factory.create_price_forecast.return_value = mock_price_forecast

    estimator = BatteryDischargeSlotEstimator(
        appdaemon_logger=mock_appdaemon_logger,
        config=config,
        forecast_factory=mock_forecast_factory,
    )

    period_start = datetime.fromisoformat("2025-10-10T16:00:00+00:00")

    battery_discharge_slot = estimator(state, period_start, period_hours=6)

    mock_price_forecast.find_peak_periods.assert_called_once_with(
        period_start,
        6,
        config.battery_export_threshold_price,
    )
    mock_production_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)
    mock_consumption_forecast.estimate_energy_kwh.assert_called_once_with(period_start, 6)

    assert len(battery_discharge_slot) == 2
    assert battery_discharge_slot[0] == BatteryDischargeSlot(
        start_time=time(20, 0), end_time=time(21, 0), current=BatteryCurrent(80.00)
    )
    assert battery_discharge_slot[1] == BatteryDischargeSlot(
        start_time=time(19, 0), end_time=time(20, 0), current=BatteryCurrent(30.00)
    )
