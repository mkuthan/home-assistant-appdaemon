from typing import Protocol


class AppdaemonStatePublisher(Protocol):
    def set_state(
        self,
        entity_id: str,
        *,
        state: object,
        attributes: dict[str, object],
        replace: bool,
        check_existence: bool,
    ) -> object: ...
