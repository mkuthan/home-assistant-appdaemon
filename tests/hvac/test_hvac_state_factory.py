from unittest.mock import Mock

from hvac.hvac_state_factory import DefaultHvacStateFactory


def test_create(
    mock_appdaemon_logger: Mock,
    mock_appdaemon_state: Mock,
    mock_appdaemon_service: Mock,
) -> None:
    state = DefaultHvacStateFactory(
        appdaemon_logger=mock_appdaemon_logger,
        appdaemon_state=mock_appdaemon_state,
        appdaemon_service=mock_appdaemon_service,
    ).create()

    assert state is not None
