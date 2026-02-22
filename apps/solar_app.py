from datetime import time
from decimal import Decimal

import appdaemon.plugins.hass.hassapi as hass
from entities.entities import BATTERY_SOC_ENTITY, PRICE_FORECAST_ENTITY
from solar.battery_discharge_slot_estimator import BatteryDischargeSlotEstimator
from solar.battery_max_current_estimator import BatteryMaxCurrentEstimator
from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.forecast_factory import DefaultForecastFactory
from solar.solar import Solar
from solar.solar_configuration import SolarConfiguration
from solar.solar_state_factory import DefaultSolarStateFactory
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.celsius import Celsius
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice
from utils.appdaemon_utils import LoggingAppdaemonService, is_dry_run


class SolarApp(hass.Hass):
    def initialize(self) -> None:
        appdaemon_logger = self
        appdaemon_state = self
        appdaemon_service = LoggingAppdaemonService(self) if is_dry_run(self) else self

        configuration = SolarConfiguration(
            time_zone=self.get_timezone(),
            # nominal battery capacity
            battery_capacity=EnergyKwh(10.0),
            # nominal battery voltage
            battery_voltage=BatteryVoltage(52.0),
            # maximum battery discharge/charge current
            battery_maximum_current=BatteryCurrent(80.0),
            # nominal battery discharge/charge current
            battery_nominal_current=BatteryCurrent(60.0),
            # night charge current to replenish battery reserve during low tariff periods
            battery_night_charge_current=BatteryCurrent(40.0),
            # minimum reserve SOC
            battery_reserve_soc_min=BatterySoc(20.0),
            # margin above minimum reserve SOC
            battery_reserve_soc_margin=BatterySoc(8.0),
            # upper limit when charging from the grid
            battery_reserve_soc_max=BatterySoc(90.0),
            # indoor temperature setpoint to estimate heating needs
            temp_in=Celsius(20.0),
            # outdoor temperature threshold to apply heating energy consumption in eco mode
            temp_out_threshold=Celsius(2.0),
            # coefficient of heat-pump performance at 7 degrees Celsius
            heating_cop_at_7c=4.0,
            # coefficient representing building heat loss rate in kW/°C
            heating_h=0.18,
            # outdoor temperature if weather forecast isn't available
            temp_out_fallback=Celsius(2.0),
            # outdoor humidity if weather forecast isn't available
            humidity_out_fallback=80.0,
            # regular consumption when in away mode
            regular_consumption_away=EnergyKwh(0.35),
            # consumption during daytime
            regular_consumption_day=EnergyKwh(0.5),
            # consumption during evening
            regular_consumption_evening=EnergyKwh(0.8),
            # threshold for exporting PV energy, net price
            pv_export_min_price_margin=EnergyPrice.pln_per_mwh(Decimal(200)),
            # threshold for exporting battery energy, net price
            battery_export_threshold_price=EnergyPrice.pln_per_mwh(Decimal(1000)),
            # skip battery export below this threshold
            battery_export_threshold_energy=EnergyKwh(1.0),
            # start time of night low tariff period (with margin)
            night_low_tariff_time_start=time.fromisoformat("22:05:00"),
            # end time of night low tariff period (with margin)
            night_low_tariff_time_end=time.fromisoformat("06:55:00"),
            # start time of day low tariff period (with margin)
            day_low_tariff_time_start=time.fromisoformat("13:05:00"),
            # end time of day low tariff period (with margin)
            day_low_tariff_time_end=time.fromisoformat("15:55:00"),
        )

        state_factory = DefaultSolarStateFactory(appdaemon_logger, appdaemon_state)
        forecast_factory = DefaultForecastFactory(appdaemon_logger, configuration)

        self.solar = Solar(
            appdaemon_logger=appdaemon_logger,
            appdaemon_service=appdaemon_service,
            configuration=configuration,
            state_factory=state_factory,
            battery_max_current_estimator=BatteryMaxCurrentEstimator(appdaemon_logger, configuration),
            battery_discharge_slot_estimator=BatteryDischargeSlotEstimator(
                appdaemon_logger, configuration, forecast_factory
            ),
            battery_reserve_soc_estimator=BatteryReserveSocEstimator(appdaemon_logger, configuration, forecast_factory),
            storage_mode_estimator=StorageModeEstimator(appdaemon_logger, configuration, forecast_factory),
        )

        self.listen_event(self.solar_debug, "SOLAR_DEBUG")

        self.log("Setting up battery reserve SoC control")
        self.run_every(self.control_battery_reserve_soc, "00:00:00", 5 * 60)

        self.log("Setting up battery max charge current control")
        self.run_every(self.control_battery_max_charge_current, "00:00:00", 5 * 60)

        self.log("Setting up battery max discharge current control")
        self.run_every(self.control_battery_max_discharge_current, "00:00:00", 5 * 60)

        self.log("Setting up storage mode control triggers")
        self.listen_state(
            self.control_storage_mode,
            [
                BATTERY_SOC_ENTITY,
                PRICE_FORECAST_ENTITY,
            ],
            constrain_start_time="sunrise +01:00:00",
            constrain_end_time="sunset -01:00:00",
        )

        self.log("Setting up battery discharge schedule")
        self.run_daily(self.schedule_battery_discharge, "15:30:00")
        self.run_daily(self.schedule_battery_discharge, "16:00:00")  # backup call

        self.log("Setting up battery discharge disable")
        self.run_daily(self.disable_battery_discharge, "22:00:00")
        self.run_daily(self.disable_battery_discharge, "22:30:00")  # backup call

        self.log("Initial battery reserve SoC control run")
        self.solar.control_battery_reserve_soc(self.get_now())

        self.log("Initial battery max charge current control run")
        self.solar.control_battery_max_charge_current(self.get_now())

        self.log("Initial battery max discharge current control run")
        self.solar.control_battery_max_discharge_current(self.get_now())

    def solar_debug(self, event_type, data, **kwargs) -> None:  # noqa: ANN001, ANN003, ARG002
        self.solar.log_state()

    def control_battery_reserve_soc(self, **kwargs: object) -> None:  # noqa: ARG002
        self.solar.control_battery_reserve_soc(self.get_now())

    def control_battery_max_charge_current(self, **kwargs: object) -> None:  # noqa: ARG002
        self.solar.control_battery_max_charge_current(self.get_now())

    def control_battery_max_discharge_current(self, **kwargs: object) -> None:  # noqa: ARG002
        self.solar.control_battery_max_discharge_current(self.get_now())

    def control_storage_mode(self, entity, attribute, old, new, **kwargs) -> None:  # noqa: ANN001, ANN003, ARG002
        self.solar.control_storage_mode(self.get_now())

    def schedule_battery_discharge(self, **kwargs: object) -> None:  # noqa: ARG002
        self.solar.schedule_battery_discharge(self.get_now())

    def disable_battery_discharge(self, **kwargs: object) -> None:  # noqa: ARG002
        self.solar.disable_battery_discharge()
