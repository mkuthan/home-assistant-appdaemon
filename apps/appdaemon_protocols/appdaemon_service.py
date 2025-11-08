from typing import Protocol

import appdaemon.plugins.hass.hassapi as hass


class AppdaemonService(Protocol):
    def call_service(self, *args, **kwargs) -> object: ...  # noqa: ANN002, ANN003
    def service_call_callback(self, result: dict) -> None: ...


class DefaultAppdaemonService:
    def __init__(self, hass: hass.Hass) -> None:
        self.hass = hass

    def call_service(self, *args, **kwargs) -> object:  # noqa: ANN002, ANN003
        return self.hass.call_service(*args, **kwargs)

    def service_call_callback(self, result: dict) -> None:
        match result:
            case {"success": True}:
                self.hass.log(f"Service call succeeded: {result}")
            case _:
                self.hass.error(f"Service call failed: {result}")


class LoggingAppdaemonService:
    def __init__(self, hass: hass.Hass) -> None:
        self.hass = hass

    def call_service(self, *args, **kwargs) -> object:  # noqa: ANN002, ANN003
        service = args[0] if args else "unknown"
        self.hass.log(f"[DRY RUN] call_service: {service} | kwargs: {kwargs}")
        return None

    def service_call_callback(self, result: dict) -> None:
        self.hass.log(f"[DRY RUN] service_call_callback: {result}")
