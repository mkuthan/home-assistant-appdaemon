# Input boolean entities
ECO_MODE_ENTITY = "input_boolean.eco_mode"
AWAY_MODE_ENTITY = "input_boolean.away_mode"

# HVAC entities
DHW_ENTITY = "water_heater.panasonic_heat_pump_main_dhw_target_temp"
HEATING_ENTITY = "climate.panasonic_heat_pump_main_z1_temp"
COOLING_ENTITY = "climate.panasonic_heat_pump_main_z1_temp_cooling"
TEMPERATURE_ADJUSTMENT_ENTITY = "number.heat_pump_temperature_adjustment"

# Solar/Battery entities
BATTERY_SOC_ENTITY = "sensor.solis_remaining_battery_capacity"
BATTERY_RESERVE_SOC_ENTITY = "number.solis_control_battery_reserve_soc"
INVERTER_STORAGE_MODE_ENTITY = "select.solis_control_storage_mode"
SLOT1_DISCHARGE_ENABLED_ENTITY = "switch.solis_control_slot1_discharge"
SLOT1_DISCHARGE_TIME_ENTITY = "text.solis_control_slot1_discharge_time"
SLOT1_DISCHARGE_CURRENT_ENTITY = "number.solis_control_slot1_discharge_current"
SLOT2_DISCHARGE_ENABLED_ENTITY = "switch.solis_control_slot2_discharge"
SLOT2_DISCHARGE_TIME_ENTITY = "text.solis_control_slot2_discharge_time"
SLOT2_DISCHARGE_CURRENT_ENTITY = "number.solis_control_slot2_discharge_current"

# Weather and temperature entities
INDOOR_TEMPERATURE_ENTITY = "sensor.heishamon_z1_actual_temperature"
OUTDOOR_TEMPERATURE_ENTITY = "sensor.heishamon_outside_ambient_temperature"
WEATHER_FORECAST_ENTITY = "weather.forecast_wieprz"

# Energy price entities
HOURLY_PRICE_ENTITY = "sensor.rce"

# Solar forecast entities
PV_FORECAST_TODAY_ENTITY = "sensor.solcast_pv_forecast_forecast_today"
PV_FORECAST_TOMORROW_ENTITY = "sensor.solcast_pv_forecast_forecast_tomorrow"


def is_heating_enabled(state: str) -> bool:
    return state.lower() == "heat"


def is_cooling_enabled(state: str) -> bool:
    return state.lower() == "cool"


def get_slot_discharge_time_entity(slot: int) -> str:
    match slot:
        case 1:
            return SLOT1_DISCHARGE_TIME_ENTITY
        case 2:
            return SLOT2_DISCHARGE_TIME_ENTITY
        case _:
            raise ValueError(f"Invalid slot: {slot}. Must be 1 or 2.")


def get_slot_discharge_current_entity(slot: int) -> str:
    match slot:
        case 1:
            return SLOT1_DISCHARGE_CURRENT_ENTITY
        case 2:
            return SLOT2_DISCHARGE_CURRENT_ENTITY
        case _:
            raise ValueError(f"Invalid slot: {slot}. Must be 1 or 2.")


def get_slot_discharge_enabled_entity(slot: int) -> str:
    match slot:
        case 1:
            return SLOT1_DISCHARGE_ENABLED_ENTITY
        case 2:
            return SLOT2_DISCHARGE_ENABLED_ENTITY
        case _:
            raise ValueError(f"Invalid slot: {slot}. Must be 1 or 2.")
