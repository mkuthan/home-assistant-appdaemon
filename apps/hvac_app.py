from datetime import time

import appdaemon.plugins.hass.hassapi as hass
from entities.entities import COOLING_ENTITY, ECO_MODE_ENTITY, HEATING_ENTITY, TEMPERATURE_ADJUSTMENT_ENTITY
from hvac.cooling_estimator import CoolingEstimator
from hvac.dhw_estimator import DhwEstimator
from hvac.heating_estimator import HeatingEstimator
from hvac.hvac import Hvac
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state_factory import DefaultHvacStateFactory
from units.celsius import Celsius
from utils.appdaemon_utils import LoggingAppdaemonService, is_dry_run


class HvacApp(hass.Hass):
    def initialize(self) -> None:
        appdaemon_logger = self
        appdaemon_state = self
        appdaemon_service = LoggingAppdaemonService(self) if is_dry_run(self) else self

        configuration = HvacConfiguration(
            time_zone=self.get_timezone(),
            # domestic hot water temperature
            dhw_temp_eco_off=Celsius(48.0),
            # domestic hot water temperature in eco mode
            dhw_temp_eco_on=Celsius(40.0),
            # when to start boosting DHW depends on temperature difference
            dhw_delta_temp=Celsius(6.0),
            # 5 minutes after low tariff starts to avoid clocks drift issues
            dhw_boost_start=time.fromisoformat("13:05:00"),
            # 5 minutes before high tariff starts to avoid clocks drift issues
            dhw_boost_end=time.fromisoformat("15:55:00"),
            # heating temperature
            heating_temp_eco_off=Celsius(20.0),
            # heating temperature in eco mode
            heating_temp_eco_on=Celsius(18.0),
            # 5 minutes after low tariff starts to avoid clocks drift issues
            heating_boost_time_start_eco_on=time.fromisoformat("22:05:00"),
            # 5 minutes before high tariff starts to avoid clocks drift issues
            heating_boost_time_end_eco_on=time.fromisoformat("06:55:00"),
            # 1 hour before wake up time
            heating_boost_time_start_eco_off=time.fromisoformat("05:00:00"),
            # 1 hour before bed time
            heating_boost_time_end_eco_off=time.fromisoformat("21:00:00"),
            # cooling temperature
            cooling_temp_eco_off=Celsius(24.0),
            # cooling temperature in eco mode
            cooling_temp_eco_on=Celsius(26.0),
            # cool when there is plenty of solar energy
            cooling_boost_time_start_eco_on=time.fromisoformat("12:00:00"),
            cooling_boost_time_end_eco_on=time.fromisoformat("16:00:00"),
            # extends cooling period a bit when eco mode is off
            cooling_boost_time_start_eco_off=time.fromisoformat("10:00:00"),
            cooling_boost_time_end_eco_off=time.fromisoformat("18:00:00"),
        )

        state_factory = DefaultHvacStateFactory(appdaemon_logger, appdaemon_state)

        self.hvac = Hvac(
            appdaemon_logger=appdaemon_logger,
            appdaemon_service=appdaemon_service,
            configuration=configuration,
            state_factory=state_factory,
            dhw_estimator=DhwEstimator(appdaemon_logger, configuration),
            heating_estimator=HeatingEstimator(appdaemon_logger, configuration),
            cooling_estimator=CoolingEstimator(appdaemon_logger, configuration),
        )

        self.log("Setting up HVAC control")
        self.run_every(self.control_scheduled, "00:00:00", 5 * 60)

        self.log("Setting up HVAC control triggers")
        self.listen_state(
            self.control_triggered,
            [
                ECO_MODE_ENTITY,
                TEMPERATURE_ADJUSTMENT_ENTITY,
                HEATING_ENTITY,  # on/off changes
                COOLING_ENTITY,  # on/off changes
            ],
        )

        self.log("Initial HVAC control run")
        self.hvac.control(self.get_now())

    def control_scheduled(self, **kwargs: dict) -> None:  # noqa: ARG002
        self.hvac.control(self.get_now())

    def control_triggered(self, entity, attribute, old, new, **kwargs) -> None:  # noqa: ANN001, ANN003, ARG002
        self.hvac.control(self.get_now())
