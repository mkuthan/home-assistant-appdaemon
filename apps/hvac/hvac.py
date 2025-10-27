from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from hvac.hvac_configuration import HvacConfiguration
from hvac.hvac_state_factory import HvacStateFactory


class Hvac:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        appdaemon_service: AppdaemonService,
        config: HvacConfiguration,
        state_factory: HvacStateFactory,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_service = appdaemon_service
        self.config = config
        self.state_factory = state_factory
