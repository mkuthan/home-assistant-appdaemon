from base_app import BaseApp
from hvac.hvac import Hvac
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state_factory import DefaultHvacStateFactory
from units.celsius import Celsius


class HvacApp(BaseApp):
    def initialize(self) -> None:
        appdaemon_logger = self
        appdaemon_state = self
        appdaemon_service = self

        config = HvacConfiguration(
            dhw_temp=Celsius(48.0),
            dhw_temp_eco=Celsius(40.0),
            dhw_boost_delta_temp=Celsius(8.0),
            dhw_boost_delta_temp_eco=Celsius(4.0),
            heating_temp=Celsius(21.0),
            heating_temp_eco=Celsius(20.0),
            heating_reduced_delta_temp=Celsius(1.0),
            heating_reduced_delta_temp_eco=Celsius(2.0),
            cooling_temp=Celsius(24.0),
            cooling_temp_eco=Celsius(26.0),
            cooling_reduced_delta_temp=Celsius(2.0),
            cooling_reduced_delta_temp_eco=Celsius(2.0),
        )

        state_factory = DefaultHvacStateFactory(
            appdaemon_logger=appdaemon_logger,
            appdaemon_state=appdaemon_state,
            appdaemon_service=appdaemon_service,
        )

        self.hvac = Hvac(
            appdaemon_logger=appdaemon_logger,
            appdaemon_service=appdaemon_service,
            config=config,
            state_factory=state_factory,
        )
