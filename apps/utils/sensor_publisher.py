import logging
import re
from datetime import datetime, time
from typing import Protocol

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_state_publisher import AppdaemonStatePublisher


class SensorPublisher(Protocol):
    def publish(self, name: str, state: object, attributes: dict[str, object]) -> None: ...


class DefaultSensorPublisher:
    _NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")

    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        appdaemon_state_publisher: AppdaemonStatePublisher,
        app_name: str,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_state_publisher = appdaemon_state_publisher
        self.app_name = self._validate_name(app_name)

    def publish(self, name: str, state: object, attributes: dict[str, object]) -> None:
        # Entity id is built here, so callers can't overwrite entities outside the dedicated namespace
        entity_id = f"sensor.appdaemon_{self.app_name}_{self._validate_name(name)}"
        try:
            self.appdaemon_state_publisher.set_state(
                entity_id,
                state=state,
                attributes={key: self._to_attribute_value(value) for key, value in attributes.items()},
                # Drop attributes left over from a different decision path
                replace=True,
                check_existence=False,
            )
        # Diagnostics must never break battery or inverter control, so fail open
        except Exception as e:
            self.appdaemon_logger.log("Failed to publish sensor %s: %s", entity_id, e, level=logging.WARNING)

    def _validate_name(self, name: str) -> str:
        if not self._NAME_PATTERN.match(name):
            raise ValueError(f"Invalid sensor name: {name!r}")
        return name

    @staticmethod
    def _to_attribute_value(value: object) -> object:
        if isinstance(value, datetime | time):
            return value.isoformat()
        # Units render the same way as in logs, e.g. "1.50kWh"
        if value is None or isinstance(value, int | float | str | bool):
            return value
        return str(value)
