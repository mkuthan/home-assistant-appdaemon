import logging
from datetime import datetime, time
from unittest.mock import ANY, Mock

import pytest
from units.battery_soc import BatterySoc
from units.energy_kwh import EnergyKwh
from utils.sensor_publisher import DefaultSensorPublisher


@pytest.fixture
def sensor_publisher(mock_appdaemon_logger: Mock, mock_appdaemon_state: Mock) -> DefaultSensorPublisher:
    return DefaultSensorPublisher(mock_appdaemon_logger, mock_appdaemon_state, "solar")


def test_publish(sensor_publisher: DefaultSensorPublisher, mock_appdaemon_state: Mock) -> None:
    sensor_publisher.publish(
        "battery_reserve_soc",
        65.0,
        {
            "energy_reserve": EnergyKwh(4.0),
            "battery_soc": BatterySoc(50.0),
            "decay_rate": 0.02,
            "reason": "use target",
            "price": None,
            "estimated_at": datetime.fromisoformat("2025-10-03T10:00:00+00:00"),
            "window_start": time(7, 0),
        },
    )

    mock_appdaemon_state.set_state.assert_called_once_with(
        "sensor.appdaemon_solar_battery_reserve_soc",
        state=65.0,
        attributes={
            "energy_reserve": "4.00kWh",
            "battery_soc": "50.00%",
            "decay_rate": 0.02,
            "reason": "use target",
            "price": None,
            "estimated_at": "2025-10-03T10:00:00+00:00",
            "window_start": "07:00:00",
        },
        replace=True,
        check_existence=False,
    )


@pytest.mark.parametrize("name", ["Upper", "with-dash", "sensor.other", ""])
def test_publish_invalid_name(sensor_publisher: DefaultSensorPublisher, mock_appdaemon_state: Mock, name: str) -> None:
    with pytest.raises(ValueError, match="Invalid sensor name"):
        sensor_publisher.publish(name, 1.0, {})

    mock_appdaemon_state.set_state.assert_not_called()


def test_publish_set_state_failure(
    sensor_publisher: DefaultSensorPublisher, mock_appdaemon_logger: Mock, mock_appdaemon_state: Mock
) -> None:
    mock_appdaemon_state.set_state.side_effect = RuntimeError("connection lost")

    sensor_publisher.publish("battery_reserve_soc", 65.0, {})

    mock_appdaemon_logger.log.assert_called_once_with(
        "Failed to publish sensor %s: %s", "sensor.appdaemon_solar_battery_reserve_soc", ANY, level=logging.WARNING
    )


def test_invalid_app_name(mock_appdaemon_logger: Mock, mock_appdaemon_state: Mock) -> None:
    with pytest.raises(ValueError, match="Invalid sensor name"):
        DefaultSensorPublisher(mock_appdaemon_logger, mock_appdaemon_state, "Solar App")
