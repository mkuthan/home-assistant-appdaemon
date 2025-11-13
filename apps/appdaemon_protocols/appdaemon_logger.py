import logging
from typing import Protocol


class AppdaemonLogger(Protocol):
    def log(self, msg: str, *args, level: str | int = logging.INFO) -> None: ...  # noqa: ANN002
