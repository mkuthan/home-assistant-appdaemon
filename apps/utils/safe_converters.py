def safe_float(value: object) -> float | None:
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return None


def safe_int(value: object) -> int | None:
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return None


def safe_bool(value: object) -> bool | None:
    value_lower = str(value).lower()
    if value_lower in ("on", "true", "1", "yes"):
        return True
    if value_lower in ("off", "false", "0", "no"):
        return False
    return None


def safe_str(value: object) -> str | None:
    if value is None:
        return None
    if str(value) == "" or str(value) == "unknown" or str(value) == "unavailable":
        return None
    return str(value)


def safe_dict(value: object) -> dict | None:
    if isinstance(value, dict):
        return value
    return None


def safe_list(value: object) -> list | None:
    if isinstance(value, list):
        return value
    return None
