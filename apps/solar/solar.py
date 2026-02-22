import logging
from datetime import datetime

from appdaemon_protocols.appdaemon_logger import AppdaemonLogger
from appdaemon_protocols.appdaemon_service import AppdaemonService
from entities.entities import (
    BATTERY_MAX_CHARGE_CURRENT_ENTITY,
    BATTERY_MAX_DISCHARGE_CURRENT_ENTITY,
    BATTERY_RESERVE_SOC_ENTITY,
    INVERTER_STORAGE_MODE_ENTITY,
    SLOT1_DISCHARGE_CURRENT_ENTITY,
    SLOT1_DISCHARGE_ENABLED_ENTITY,
    SLOT1_DISCHARGE_TIME_ENTITY,
)
from solar.battery_discharge_slot_estimator import BatteryDischargeSlotEstimator
from solar.battery_max_current_estimator import BatteryMaxCurrentEstimator
from solar.battery_reserve_soc_estimator import BatteryReserveSocEstimator
from solar.solar_configuration import SolarConfiguration
from solar.solar_state import SolarState
from solar.solar_state_factory import SolarStateFactory
from solar.storage_mode import StorageMode
from solar.storage_mode_estimator import StorageModeEstimator
from units.battery_current import BatteryCurrent
from units.battery_soc import BatterySoc
from utils.appdaemon_utils import LoggingAppdaemonCallback


class Solar:
    def __init__(
        self,
        appdaemon_logger: AppdaemonLogger,
        appdaemon_service: AppdaemonService,
        configuration: SolarConfiguration,
        state_factory: SolarStateFactory,
        battery_max_current_estimator: BatteryMaxCurrentEstimator,
        battery_discharge_slot_estimator: BatteryDischargeSlotEstimator,
        battery_reserve_soc_estimator: BatteryReserveSocEstimator,
        storage_mode_estimator: StorageModeEstimator,
    ) -> None:
        self.appdaemon_logger = appdaemon_logger
        self.appdaemon_service = appdaemon_service
        self.configuration = configuration
        self.state_factory = state_factory
        self.battery_max_current_estimator = battery_max_current_estimator
        self.battery_discharge_slot_estimator = battery_discharge_slot_estimator
        self.battery_reserve_soc_estimator = battery_reserve_soc_estimator
        self.storage_mode_estimator = storage_mode_estimator

    def log_state(self) -> None:
        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.log("Unknown state, cannot log state", level=logging.WARNING)
        else:
            self.appdaemon_logger.log("Current state: %s", state)

    def control_battery_reserve_soc(self, now: datetime) -> None:
        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.log("Unknown state, cannot control battery reserve SoC", level=logging.WARNING)
            return

        battery_reserve_soc = self.battery_reserve_soc_estimator.estimate_battery_reserve_soc(state, now)

        if battery_reserve_soc is not None:
            self.appdaemon_logger.log(
                "Change battery reserve SoC from %s to %s", state.battery_reserve_soc, battery_reserve_soc
            )
            self._set_battery_reserve_soc(battery_reserve_soc)

    def control_battery_max_charge_current(self, now: datetime) -> None:
        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.log("Unknown state, cannot control battery max charge current", level=logging.WARNING)
            return
        battery_max_charge_current = self.battery_max_current_estimator.estimate_battery_max_charge_current(state, now)
        if battery_max_charge_current is not None:
            self.appdaemon_logger.log(
                "Change battery max charge current from %s to %s",
                state.battery_max_charge_current,
                battery_max_charge_current,
            )
            self._set_battery_max_charge_current(battery_max_charge_current)

    def control_battery_max_discharge_current(self, now: datetime) -> None:
        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.log(
                "Unknown state, cannot control battery max discharge current", level=logging.WARNING
            )
            return
        battery_max_discharge_current = self.battery_max_current_estimator.estimate_battery_max_discharge_current(
            state, now
        )
        if battery_max_discharge_current is not None:
            self.appdaemon_logger.log(
                "Change battery max discharge current from %s to %s",
                state.battery_max_discharge_current,
                battery_max_discharge_current,
            )
            self._set_battery_max_discharge_current(battery_max_discharge_current)

    def control_storage_mode(self, now: datetime) -> None:
        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.log("Unknown state, cannot control storage mode", level=logging.WARNING)
            return

        storage_mode = self.storage_mode_estimator.estimate_storage_mode(state, now)

        if storage_mode is not None:
            self.appdaemon_logger.log("Change storage mode from %s to %s", state.inverter_storage_mode, storage_mode)
            self._set_storage_mode(storage_mode)

    def schedule_battery_discharge(self, now: datetime) -> None:
        self.appdaemon_logger.log("Schedule battery discharge at 4 PM")

        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.log("Unknown state, cannot schedule battery discharge", level=logging.WARNING)
            return

        estimated_battery_discharge_slot = self.battery_discharge_slot_estimator.estimate_battery_discharge_at_4_pm(
            state, now
        )

        if estimated_battery_discharge_slot is not None:
            self._set_slot1_discharge(
                state,
                estimated_battery_discharge_slot.time_str(),
                estimated_battery_discharge_slot.current,
            )
            self._enable_slot1_discharge(state)
        else:
            self._disable_slot1_discharge(state)

    def disable_battery_discharge(self) -> None:
        self.appdaemon_logger.log("Disable battery discharge")

        if (state := self.state_factory.create()) is None:
            self.appdaemon_logger.log("Unknown state, cannot disable battery discharge", level=logging.WARNING)
            return

        self._disable_slot1_discharge(state)

    def _set_battery_reserve_soc(self, battery_reserve_soc: BatterySoc) -> None:
        self.appdaemon_service.call_service(
            "number/set_value",
            callback=LoggingAppdaemonCallback(self.appdaemon_logger),
            entity_id=BATTERY_RESERVE_SOC_ENTITY,
            value=battery_reserve_soc.value,
        )

    def _set_battery_max_charge_current(self, battery_max_charge_current: BatteryCurrent) -> None:
        self.appdaemon_service.call_service(
            "number/set_value",
            callback=LoggingAppdaemonCallback(self.appdaemon_logger),
            entity_id=BATTERY_MAX_CHARGE_CURRENT_ENTITY,
            value=battery_max_charge_current.value,
        )

    def _set_battery_max_discharge_current(self, battery_max_discharge_current: BatteryCurrent) -> None:
        self.appdaemon_service.call_service(
            "number/set_value",
            callback=LoggingAppdaemonCallback(self.appdaemon_logger),
            entity_id=BATTERY_MAX_DISCHARGE_CURRENT_ENTITY,
            value=battery_max_discharge_current.value,
        )

    def _set_storage_mode(self, storage_mode: StorageMode) -> None:
        self.appdaemon_service.call_service(
            "select/select_option",
            callback=LoggingAppdaemonCallback(self.appdaemon_logger),
            entity_id=INVERTER_STORAGE_MODE_ENTITY,
            option=storage_mode.value,
        )

    def _set_slot1_discharge(self, state: SolarState, discharge_time: str, discharge_current: BatteryCurrent) -> None:
        current_discharge_time = state.slot1_discharge_time
        if current_discharge_time != discharge_time:
            self.appdaemon_logger.log(
                "Change slot1 battery discharge time from %s to %s",
                current_discharge_time,
                discharge_time,
            )
            self.appdaemon_service.call_service(
                "text/set_value",
                callback=LoggingAppdaemonCallback(self.appdaemon_logger),
                entity_id=SLOT1_DISCHARGE_TIME_ENTITY,
                value=discharge_time,
            )
        else:
            self.appdaemon_logger.log("Slot1 battery discharge time already set to %s", current_discharge_time)

        current_discharge_current = state.slot1_discharge_current
        if current_discharge_current != discharge_current:
            self.appdaemon_logger.log(
                "Change slot1 battery discharge current from %s to %s",
                current_discharge_current,
                discharge_current,
            )
            self.appdaemon_service.call_service(
                "number/set_value",
                callback=LoggingAppdaemonCallback(self.appdaemon_logger),
                entity_id=SLOT1_DISCHARGE_CURRENT_ENTITY,
                value=discharge_current.value,
            )
        else:
            self.appdaemon_logger.log(
                "Slot1 battery discharge current already set to %s",
                current_discharge_current,
            )

    def _enable_slot1_discharge(self, state: SolarState) -> None:
        if not state.is_slot1_discharge_enabled:
            self.appdaemon_logger.log("Enabling slot 1 discharge")
            self.appdaemon_service.call_service(
                "switch/turn_on",
                callback=LoggingAppdaemonCallback(self.appdaemon_logger),
                entity_id=SLOT1_DISCHARGE_ENABLED_ENTITY,
            )
        else:
            self.appdaemon_logger.log("Slot 1 battery discharge is already enabled")

    def _disable_slot1_discharge(self, state: SolarState) -> None:
        if state.is_slot1_discharge_enabled:
            self.appdaemon_logger.log("Disabling slot 1 discharge")
            self.appdaemon_service.call_service(
                "switch/turn_off",
                callback=LoggingAppdaemonCallback(self.appdaemon_logger),
                entity_id=SLOT1_DISCHARGE_ENABLED_ENTITY,
            )
        else:
            self.appdaemon_logger.log("Slot 1 battery discharge is already disabled")
