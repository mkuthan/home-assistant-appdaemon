from datetime import time

import appdaemon.plugins.hass.hassapi as hass
from entities.entities import COOLING_ENTITY, ECO_MODE_ENTITY, HEATING_ENTITY
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
            dhw_temp=Celsius(48.0),
            dhw_temp_eco=Celsius(40.0),
            dhw_delta_temp=Celsius(6.0),
            dhw_boost_start=time.fromisoformat("13:05:00"),
            dhw_boost_end=time.fromisoformat("15:55:00"),
            heating_temp=Celsius(20.0),
            heating_temp_eco=Celsius(18.0),
            heating_boost_delta_temp=Celsius(1.0),
            heating_boost_delta_temp_eco=Celsius(2.0),
            heating_boost_time_start_eco_on=time.fromisoformat("22:05:00"),
            heating_boost_time_end_eco_on=time.fromisoformat("06:45:00"),
            heating_boost_time_start_eco_off=time.fromisoformat("05:00:00"),
            heating_boost_time_end_eco_off=time.fromisoformat("21:00:00"),
            cooling_temp=Celsius(24.0),
            cooling_temp_eco=Celsius(26.0),
            cooling_boost_delta_temp=Celsius(2.0),
            cooling_boost_delta_temp_eco=Celsius(2.0),
            cooling_boost_time_start_eco_on=time.fromisoformat("12:00:00"),
            cooling_boost_time_end_eco_on=time.fromisoformat("16:00:00"),
            cooling_boost_time_start_eco_off=time.fromisoformat("10:00:00"),
            cooling_boost_time_end_eco_off=time.fromisoformat("18:00:00"),
        )

        state_factory = DefaultHvacStateFactory(
            appdaemon_logger=appdaemon_logger,
            appdaemon_state=appdaemon_state,
            appdaemon_service=appdaemon_service,
        )

        self.hvac = Hvac(
            appdaemon_logger=appdaemon_logger,
            appdaemon_service=appdaemon_service,
            configuration=configuration,
            state_factory=state_factory,
            dhw_estimator=DhwEstimator(appdaemon_logger, configuration),
            heating_estimator=HeatingEstimator(appdaemon_logger, configuration),
            cooling_estimator=CoolingEstimator(appdaemon_logger, configuration),
        )

        self.log("Setting up HVAC control every 5 minutes")
        self.run_every(self.control_scheduled, "00:00:00", 5 * 60)

        self.log("Setting up HVAC control triggers")
        self.listen_state(
            self.control_triggered,
            [
                ECO_MODE_ENTITY,
                HEATING_ENTITY,  # on/off changes
                COOLING_ENTITY,  # on/off changes
            ],
        )

    def control_scheduled(self, **kwargs: dict) -> None:  # noqa: ARG002
        self.hvac.control(self.get_now())

    def control_triggered(self, entity, attribute, old, new, **kwargs) -> None:  # noqa: ANN001, ANN003, ARG002
        self.hvac.control(self.get_now())
