import logging

import appdaemon.plugins.hass.hassapi as hass
from appdaemon_protocols.appdaemon_logger import AppdaemonLogger


def is_dry_run(hass: hass.Hass) -> bool:
    return hass.config.get("dry_run", False)


class LoggingAppdaemonCallback:
    def __init__(self, appdaemon_logger: AppdaemonLogger) -> None:
        self.appdaemon_logger = appdaemon_logger

    def __call__(self, result: dict) -> None:
        match result:
            case {"success": True}:
                self.appdaemon_logger.log("Service call succeeded: %s", result)
            case _:
                self.appdaemon_logger.log("Service call failed: %s", result, level=logging.ERROR)


class LoggingAppdaemonService:
    def __init__(self, appdaemon_logger: AppdaemonLogger) -> None:
        self.appdaemon_logger = appdaemon_logger

    def call_service(self, service: str, **data) -> object:  # noqa: ANN002, ANN003
        self.appdaemon_logger.log("[DRY RUN] call_service: %s | data: %s", service, data)
        return None
