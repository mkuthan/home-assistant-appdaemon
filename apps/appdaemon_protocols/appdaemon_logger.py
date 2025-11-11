from typing import Protocol


class AppdaemonLogger(Protocol):
    def log(self, msg: str, *args, level: str = "info") -> None: ...  # noqa: ANN002
