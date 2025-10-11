from datetime import time

from units.battery_current import BatteryCurrent
from units.battery_discharge_slot import BatteryDischargeSlot


def test_time_str() -> None:
    slot = BatteryDischargeSlot(start_time=time(9, 0), end_time=time(10, 0), current=BatteryCurrent(10.0))
    assert slot.time_str() == "09:00-10:00"


def test_format() -> None:
    slot = BatteryDischargeSlot(start_time=time(9, 0), end_time=time(10, 0), current=BatteryCurrent(10.0))
    assert f"{slot}" == "09:00-10:00@10.00A"
