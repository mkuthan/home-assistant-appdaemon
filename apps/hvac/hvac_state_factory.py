from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from appdaemon_protocols.appdaemon_state import AppdaemonState
from hvac.hvac_state import HvacState


class HvacStateFactory(Protocol):
    def create(self) -> HvacState | None: ...


class DefaultHvacStateFactory:
    def __init__(
        self, appdaemon_logger: AppdaemonLogger, appdaemon_state: AppdaemonState, appdaemon_service: AppdaemonService
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_state = appdaemon_state
        self.appdaemon_service = appdaemon_service

    def create(self) -> HvacState | None:
        # TODO: Implement HVAC state creation logic
        return HvacState()
