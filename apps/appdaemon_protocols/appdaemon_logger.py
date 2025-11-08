from typing import Protocol

import appdaemon.plugins.hass.hassapi as hass


class AppdaemonLogger(Protocol):
    def debug(self, msg: str) -> None: ...

    def info(self, msg: str) -> None: ...

    def warn(self, msg: str) -> None: ...

    def error(self, msg: str) -> None: ...


class DefaultAppdaemonLogger:
    def __init__(self, hass: hass.Hass) -> None:
        self.hass = hass

    def debug(self, msg: str) -> None:
        self.hass.log(msg, level="DEBUG")

    def info(self, msg: str) -> None:
        self.hass.log(msg, level="INFO")

    def warn(self, msg: str) -> None:
        self.hass.log(msg, level="WARNING")

    def error(self, msg: str) -> None:
        self.hass.log(msg, level="ERROR")
