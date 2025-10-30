ECO_MODE_ENTITY = "input_boolean.eco_mode"

DHW_ENTITY = "water_heater.panasonic_heat_pump_main_dhw_target_temp"
HEATING_ENTITY = "climate.panasonic_heat_pump_main_z1_temp"
COOLING_ENTITY = "climate.panasonic_heat_pump_main_z1_temp_cooling"


def is_heating_enabled(state: str) -> bool:
    return state.lower() == "heat"


def is_cooling_enabled(state: str) -> bool:
    return state.lower() == "cool"
