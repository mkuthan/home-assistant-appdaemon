from typing import Protocol


class AppdaemonService(Protocol):
    def call_service(self, *args, **kwargs) -> object: ...  # noqa: ANN002, ANN003
    def service_call_callback(self, result: dict) -> None: ...
