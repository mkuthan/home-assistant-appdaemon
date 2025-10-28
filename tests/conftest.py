from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_appdaemon_logger() -> Mock:
    return Mock()


@pytest.fixture
def mock_appdaemon_state() -> Mock:
    return Mock()


@pytest.fixture
def mock_appdaemon_service() -> Mock:
    return Mock()
