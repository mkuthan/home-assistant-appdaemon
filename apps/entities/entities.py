# Input boolean entities
ECO_MODE_ENTITY = "input_boolean.eco_mode"
AWAY_MODE_ENTITY = "input_boolean.away_mode"

# HVAC entities
DHW_TEMPERATURE_ENTITY = "sensor.heishamon_tank_temperature"
INDOOR_TEMPERATURE_ENTITY = "sensor.heishamon_z1_actual_temperature"
OUTDOOR_TEMPERATURE_ENTITY = "sensor.heishamon_outside_ambient_temperature"

DHW_ENTITY = "water_heater.panasonic_heat_pump_main_dhw_target_temp"
DHW_TEMP_ENTITY = "sensor.panasonic_heat_pump_main_dhw_temp"
HEATING_ENTITY = "climate.panasonic_heat_pump_main_z1_temp"
MAIN_TEMP_ENTITY = "sensor.panasonic_heat_pump_main_z1_temp"
COOLING_ENTITY = "climate.panasonic_heat_pump_main_z1_temp_cooling"

DHW_DELTA_TEMP_ENTITY = "number.panasonic_heat_pump_main_dhw_heat_delta"

HEATING_CURVE_TARGET_HIGH_TEMP_ENTITY = "number.panasonic_heat_pump_main_z1_heat_curve_target_high_temp"
HEATING_CURVE_TARGET_LOW_TEMP_ENTITY = "number.panasonic_heat_pump_main_z1_heat_curve_target_low_temp"

TEMPERATURE_ADJUSTMENT_ENTITY = "input_number.heat_pump_temperature_adjustment"

# Solar/Battery entities
BATTERY_SOC_ENTITY = "sensor.solis_remaining_battery_capacity"
BATTERY_RESERVE_SOC_ENTITY = "number.solis_control_battery_reserve_soc"
INVERTER_STORAGE_MODE_ENTITY = "select.solis_control_storage_mode"
SLOT1_DISCHARGE_ENABLED_ENTITY = "switch.solis_control_slot1_discharge"
SLOT1_DISCHARGE_TIME_ENTITY = "text.solis_control_slot1_discharge_time"
SLOT1_DISCHARGE_CURRENT_ENTITY = "number.solis_control_slot1_discharge_current"

# Weather entities
WEATHER_FORECAST_ENTITY = "sensor.weather_forecast"

# Energy price entities
PRICE_FORECAST_ENTITY = "sensor.rce_pse_price"

# Solar forecast entities
PV_FORECAST_TODAY_ENTITY = "sensor.solcast_pv_forecast_forecast_today"
PV_FORECAST_TOMORROW_ENTITY = "sensor.solcast_pv_forecast_forecast_tomorrow"


def is_heating_enabled(state: str) -> bool:
    return state.lower() == "heat"


def is_cooling_enabled(state: str) -> bool:
    return state.lower() == "cool"
