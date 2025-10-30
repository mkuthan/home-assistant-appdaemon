import pytest
from entities.entities import is_cooling_enabled, is_heating_enabled


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("heat", True),
        ("HEAT", True),
        ("off", False),
        ("cool", False),
    ],
)
def test_is_heating_enabled(state: str, expected: bool) -> None:
    assert is_heating_enabled(state) is expected


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("cool", True),
        ("COOL", True),
        ("off", False),
        ("heat", False),
    ],
)
def test_is_cooling_enabled(state: str, expected: bool) -> None:
    assert is_cooling_enabled(state) is expected
