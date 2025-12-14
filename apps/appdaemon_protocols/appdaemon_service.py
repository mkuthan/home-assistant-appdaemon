from typing import Any, Protocol


class AppdaemonService(Protocol):
    def call_service(self, service: str, **data) -> Any: ...  # noqa: ANN002, ANN003, ANN401
