from datetime import time

from solar.battery_discharge_slot import BatteryDischargeSlot
from units.battery_current import BatteryCurrent


def test_time_str() -> None:
    slot = BatteryDischargeSlot(start_time=time(9, 0), end_time=time(10, 0), current=BatteryCurrent(10.0))
    assert slot.time_str() == "09:00-10:00"


def test_str() -> None:
    slot = BatteryDischargeSlot(start_time=time(9, 0), end_time=time(10, 0), current=BatteryCurrent(10.0))
    assert f"{slot}" == "09:00-10:00@10.00A"
