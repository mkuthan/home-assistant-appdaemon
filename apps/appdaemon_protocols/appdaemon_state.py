from typing import Protocol


class AppdaemonState(Protocol):
    def get_state(self, entity_id: str, attribute: str | None = None) -> object: ...
