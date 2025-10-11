import pytest
from utils.safe_converters import safe_bool, safe_dict, safe_float, safe_int, safe_list, safe_str


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("3.14", 3.14),
        ("0", 0.0),
        ("-2.5", -2.5),
        (None, None),
        ("invalid", None),
        ("", None),
    ],
)
def test_safe_float(input_value: object, expected: float | None) -> None:
    assert safe_float(input_value) == expected


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("42", 42),
        ("0", 0),
        ("-10", -10),
        (None, None),
        ("", None),
        ("invalid", None),
        ("3.14", None),
    ],
)
def test_safe_int(input_value: object, expected: int | None) -> None:
    assert safe_int(input_value) == expected


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("on", True),
        ("off", False),
        ("true", True),
        ("false", False),
        ("1", True),
        ("0", False),
        ("yes", True),
        ("no", False),
        ("ON", True),
        ("OFF", False),
        ("True", True),
        ("False", False),
        (None, None),
        ("", None),
        ("invalid", None),
    ],
)
def test_safe_bool(input_value: object, expected: bool | None) -> None:
    assert safe_bool(input_value) == expected


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("hello", "hello"),
        ("123", "123"),
        (None, None),
        ("", None),
        ("unknown", None),
        ("unavailable", None),
    ],
)
def test_safe_str(input_value: object, expected: str | None) -> None:
    assert safe_str(input_value) == expected


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ({"key": "value"}, {"key": "value"}),
        (None, None),
        ("", None),
        ("unknown", None),
        ("unavailable", None),
    ],
)
def test_safe_dict(input_value: object, expected: object | None) -> None:
    assert safe_dict(input_value) == expected


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ([1, 2, 3], [1, 2, 3]),
        (None, None),
        ("", None),
        ("unknown", None),
        ("unavailable", None),
    ],
)
def test_safe_list(input_value: object, expected: object | None) -> None:
    assert safe_list(input_value) == expected
