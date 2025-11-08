from typing import Protocol

import appdaemon.plugins.hass.hassapi as hass


class AppdaemonState(Protocol):
    def get_state(self, entity_id: str, attribute: str | None = None) -> object: ...


class DefaultAppdaemonState:
    def __init__(self, hass: hass.Hass) -> None:
        self.hass = hass

    def get_state(self, entity_id: str, attribute: str | None = None) -> object:
        return self.hass.get_state(entity_id, attribute)
