from datetime import datetime

import appdaemon.plugins.hass.hassapi as hass


class BaseApp(hass.Hass):
    def today_at_hour(self, hour: int) -> datetime:
        return self.datetime(aware=True).replace(hour=hour, minute=0, second=0, microsecond=0)

    def debug(self, msg: str) -> None:
        self.log(msg, level="DEBUG")

    def info(self, msg: str) -> None:
        self.log(msg, level="INFO")

    def warn(self, msg: str) -> None:
        self.log(msg, level="WARNING")

    def error(self, msg: str) -> None:
        self.log(msg, level="ERROR")

    def service_call_callback(self, result: dict) -> None:
        match result:
            case {"success": True}:
                self.info(f"Service call succeeded: {result}")
            case _:
                self.error(f"Service call failed: {result}")
