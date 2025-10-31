from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from entities.entities import (
    BATTERY_RESERVE_SOC_ENTITY,
    INVERTER_STORAGE_MODE_ENTITY,
    get_slot_discharge_current_entity,
    get_slot_discharge_enabled_entity,
    get_slot_discharge_time_entity,
)
from solar.battery_discharge_slot_estimator import BatteryDischargeSlotEstimator
from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.solar_state_factory import SolarStateFactory
from solar.storage_mode import StorageMode
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc


class Solar:
    _NUM_DISCHARGE_SLOTS = 2

    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        appdaemon_service: AppdaemonService,
        configuration: SolarConfiguration,
        state_factory: SolarStateFactory,
        battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
        battery_reserve_soc_estimator: BatteryReserveSocEstimator,
        storage_mode_estimator: StorageModeEstimator,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_service = appdaemon_service
        self.configuration = configuration
        self.state_factory = state_factory
        self.battery_discharge_slot_estimator = battery_discharge_slot_estimator
        self.battery_reserve_soc_estimator = battery_reserve_soc_estimator
        self.storage_mode_estimator = storage_mode_estimator

    def log_state(self) -> None:
        state = self.state_factory.create()
        if state is None:
            self.appdaemon_logger.warn("Unknown state, cannot log state")
        else:
            self.appdaemon_logger.info(f"Current state: {state}")

    def control_battery_reserve_soc(self, now: datetime) -> None:
        state = self.state_factory.create()
        if state is None:
            self.appdaemon_logger.warn("Unknown state, cannot control battery reserve SoC")
            return

        battery_reserve_soc = self.battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

        if battery_reserve_soc is not None:
            self._set_battery_reserve_soc(state, battery_reserve_soc)

    def control_storage_mode(self, now: datetime) -> None:
        state = self.state_factory.create()
        if state is None:
            self.appdaemon_logger.warn("Unknown state, cannot control storage mode")
            return

        storage_mode = self.storage_mode_estimator.estimate_storage_mode(state, now)

        if storage_mode is not None:
            self._set_storage_mode(state, storage_mode)

    def schedule_battery_discharge(self, now: datetime) -> None:
        self.appdaemon_logger.info("Schedule battery discharge at 4 PM")

        state = self.state_factory.create()
        if state is None:
            self.appdaemon_logger.warn("Unknown state, cannot schedule battery discharge")
            return

        estimated_battery_discharge_slots = self.battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(
            state, now
        )

        for slot in range(1, self._NUM_DISCHARGE_SLOTS + 1):
            if len(estimated_battery_discharge_slots) >= slot:
                estimated_battery_discharge_slot = estimated_battery_discharge_slots[slot - 1]
                self._set_slot_discharge(
                    state,
                    slot,
                    estimated_battery_discharge_slot.time_str(),
                    estimated_battery_discharge_slot.current,
                )
                self._enable_slot_discharge(state, slot)
            else:
                self._disable_slot_discharge(state, slot)

    def disable_battery_discharge(self) -> None:
        self.appdaemon_logger.info("Disable battery discharge")

        state = self.state_factory.create()
        if state is None:
            self.appdaemon_logger.warn("Unknown state, cannot disable battery discharge")
            return

        for slot in range(1, self._NUM_DISCHARGE_SLOTS + 1):
            self._disable_slot_discharge(state, slot)

    def _set_battery_reserve_soc(self, state: SolarState, battery_reserve_soc: BatterySoc) -> None:
        self.appdaemon_logger.info(
            f"Change battery reserve SoC from {state.battery_reserve_soc} to {battery_reserve_soc}"
        )
        self.appdaemon_service.call_service(
            "number/set_value",
            callback=self.appdaemon_service.service_call_callback,
            entity_id=BATTERY_RESERVE_SOC_ENTITY,
            value=battery_reserve_soc.value,
        )

    def _set_storage_mode(self, state: SolarState, storage_mode: StorageMode) -> None:
        self.appdaemon_logger.info(f"Change storage mode from {state.inverter_storage_mode} to {storage_mode}")
        self.appdaemon_service.call_service(
            "select/select_option",
            callback=self.appdaemon_service.service_call_callback,
            entity_id=INVERTER_STORAGE_MODE_ENTITY,
            option=storage_mode.value,
        )

    def _set_slot_discharge(
        self, state: SolarState, slot: int, discharge_time: str, discharge_current: BatteryCurrent
    ) -> None:
        if not 1 <= slot <= self._NUM_DISCHARGE_SLOTS:
            self.appdaemon_logger.error(f"Invalid slot number: {slot}")
            return

        current_discharge_time = getattr(state, f"slot{slot}_discharge_time")
        if current_discharge_time != discharge_time:
            self.appdaemon_logger.info(
                f"Change slot {slot} battery discharge time from {current_discharge_time} to {discharge_time}"
            )
            self.appdaemon_service.call_service(
                "text/set_value",
                callback=self.appdaemon_service.service_call_callback,
                entity_id=get_slot_discharge_time_entity(slot),
                value=discharge_time,
            )
        else:
            self.appdaemon_logger.info(f"Slot {slot} battery discharge time already set to {current_discharge_time}")

        current_discharge_current = getattr(state, f"slot{slot}_discharge_current")
        if current_discharge_current != discharge_current:
            self.appdaemon_logger.info(
                f"Change slot {slot} battery discharge current from {current_discharge_current} to {discharge_current}"
            )
            self.appdaemon_service.call_service(
                "number/set_value",
                callback=self.appdaemon_service.service_call_callback,
                entity_id=get_slot_discharge_current_entity(slot),
                value=discharge_current.value,
            )
        else:
            self.appdaemon_logger.info(
                f"Slot {slot} battery discharge current already set to {current_discharge_current}"
            )

    def _enable_slot_discharge(self, state: SolarState, slot: int) -> None:
        if not 1 <= slot <= self._NUM_DISCHARGE_SLOTS:
            self.appdaemon_logger.error(f"Invalid slot number: {slot}")
            return

        if not getattr(state, f"is_slot{slot}_discharge_enabled"):
            self.appdaemon_logger.info(f"Enabling slot {slot} discharge")
            # slots can't be enabled concurrently, use blocking call
            result = self.appdaemon_service.call_service(
                "switch/turn_on",
                entity_id=get_slot_discharge_enabled_entity(slot),
            )
            match result:
                case {"success": True}:
                    self.appdaemon_logger.info(f"Successfully enabled slot {slot} discharge")
                case _:
                    self.appdaemon_logger.error(f"Failed to enable slot {slot} discharge: {result}")
        else:
            self.appdaemon_logger.info(f"Slot {slot} battery discharge is already enabled")

    def _disable_slot_discharge(self, state: SolarState, slot: int) -> None:
        if not 1 <= slot <= self._NUM_DISCHARGE_SLOTS:
            self.appdaemon_logger.error(f"Invalid slot number: {slot}")
            return

        if getattr(state, f"is_slot{slot}_discharge_enabled"):
            self.appdaemon_logger.info(f"Disabling slot {slot} discharge")
            # slots can't be disabled concurrently, use blocking call
            result = self.appdaemon_service.call_service(
                "switch/turn_off",
                entity_id=get_slot_discharge_enabled_entity(slot),
            )
            match result:
                case {"success": True}:
                    self.appdaemon_logger.info(f"Successfully disabled slot {slot} discharge")
                case _:
                    self.appdaemon_logger.error(f"Failed to disable slot {slot} discharge: {result}")
        else:
            self.appdaemon_logger.info(f"Slot {slot} battery discharge is already disabled")
