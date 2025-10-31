from datetime import time
from decimal import Decimal

from base_app import BaseApp
from entities.entities import BATTERY_SOC_ENTITY, HOURLY_PRICE_ENTITY
from solar.battery_discharge_slot_estimator import BatteryDischargeSlotEstimator
from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.forecast_factory import DefaultForecastFactory
from solar.solar import Solar
from solar.solar_configuration import SolarConfiguration
from solar.solar_state_factory import DefaultSolarStateFactory
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from units.battery_voltage import BatteryVoltage
from units.energy_kwh import EnergyKwh
from units.energy_price import EnergyPrice


class SolarApp(BaseApp):
    def initialize(self) -> None:
        appdaemon_logger = self
        appdaemon_state = self
        appdaemon_service = self

        configuration = SolarConfiguration(
            battery_capacity=EnergyKwh(10.0),
            battery_voltage=BatteryVoltage(52.0),
            battery_maximum_current=BatteryCurrent(80.0),
            battery_reserve_soc_min=BatterySoc(20.0),
            battery_reserve_soc_margin=BatterySoc(8.0),
            battery_reserve_soc_max=BatterySoc(95.0),
            temp_in=21.0,  # °C
            heating_cop_at_7c=4.0,  # ratio
            heating_h=0.18,  # kW/°C
            temp_out_fallback=5.0,  # °C
            humidity_out_fallback=80.0,  # %
            regular_consumption_away=EnergyKwh(0.35),
            regular_consumption_day=EnergyKwh(0.6),
            regular_consumption_evening=EnergyKwh(0.8),
            pv_export_min_price_margin=EnergyPrice.pln_per_mwh(Decimal(200)),
            battery_export_threshold_price=EnergyPrice.pln_per_mwh(Decimal(1200)),
            battery_export_threshold_energy=EnergyKwh(1.0),
            night_low_tariff_time_start=time.fromisoformat("22:05:00"),
            night_low_tariff_time_end=time.fromisoformat("06:55:00"),
            day_low_tariff_time_start=time.fromisoformat("13:05:00"),
            day_low_tariff_time_end=time.fromisoformat("15:55:00"),
        )

        state_factory = DefaultSolarStateFactory(appdaemon_logger, appdaemon_state, appdaemon_service)
        forecast_factory = DefaultForecastFactory(appdaemon_logger, configuration)

        self.solar = Solar(
            appdaemon_logger=appdaemon_logger,
            appdaemon_service=appdaemon_service,
            configuration=configuration,
            state_factory=state_factory,
            battery_discharge_slot_estimator=BatteryDischargeSlotEstimator(
                appdaemon_logger, configuration, forecast_factory
            ),
            battery_reserve_soc_estimator=BatteryReserveSocEstimator(appdaemon_logger, configuration, forecast_factory),
            storage_mode_estimator=StorageModeEstimator(appdaemon_logger, configuration, forecast_factory),
        )

        self.listen_event(self.solar_debug, "SOLAR_DEBUG")

        self.info("Scheduling battery reserve SoC control every 5 minutes")
        self.run_every(self.control_battery_reserve_soc, "00:00:00", 5 * 60)

        self.info("Setting up storage mode control triggers on relevant state changes")
        self.listen_state(
            self.control_storage_mode,
            [
                BATTERY_SOC_ENTITY,
                HOURLY_PRICE_ENTITY,
            ],
            constrain_start_time="sunrise +01:00:00",
            constrain_end_time="sunset -01:00:00",
        )

        self.info("Scheduling battery discharge schedule")
        self.run_daily(self.schedule_battery_discharge, "15:30:00")
        self.run_daily(self.schedule_battery_discharge, "16:00:00")  # backup call

        self.info("Scheduling battery discharge disable")
        self.run_daily(self.disable_battery_discharge, "22:00:00")
        self.run_daily(self.disable_battery_discharge, "22:05:00")  # backup call

    def solar_debug(self, event_type, data, **kwargs) -> None:  # noqa: ANN001, ANN003, ARG002
        self.solar.log_state()

    def control_battery_reserve_soc(self, **_kwargs: object) -> None:
        self.solar.control_battery_reserve_soc(self.get_now())

    def control_storage_mode(self, entity, attribute, old, new, **kwargs) -> None:  # noqa: ANN001, ANN003, ARG002
        self.solar.control_storage_mode(self.get_now())

    def schedule_battery_discharge(self, **_kwargs: object) -> None:
        self.solar.schedule_battery_discharge(self.get_now())

    def disable_battery_discharge(self, **_kwargs: object) -> None:
        self.solar.disable_battery_discharge()
