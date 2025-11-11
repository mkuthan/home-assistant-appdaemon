from typing import Protocol


class AppdaemonService(Protocol):
    def call_service(self, service: str, **data) -> object: ...  # noqa: ANN002, ANN003
