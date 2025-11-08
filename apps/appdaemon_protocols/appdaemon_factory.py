import appdaemon.plugins.hass.hassapi as hass
from appdaemon_protocols.appdaemon_logger import AppdaemonLogger, DefaultAppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService, DefaultAppdaemonService, LoggingAppdaemonService
from appdaemon_protocols.appdaemon_state import AppdaemonState, DefaultAppdaemonState


def create_appdaemon_service(hass: hass.Hass) -> AppdaemonService:
    dry_run = hass.config.get("dry_run", False)
    if dry_run:
        return LoggingAppdaemonService(hass=hass)
    else:
        return DefaultAppdaemonService(hass=hass)


def create_appdaemon_logger(hass: hass.Hass) -> AppdaemonLogger:
    return DefaultAppdaemonLogger(hass=hass)


def create_appdaemon_state(hass: hass.Hass) -> AppdaemonState:
    return DefaultAppdaemonState(hass=hass)
