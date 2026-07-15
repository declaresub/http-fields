from typing import Any

import pytest

from http_headers import ContentRange


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "bytes 42-1233/1234",
            ContentRange(
                range_unit="bytes", first_pos=42, last_pos=1233, complete_length=1234
            ),
        ),
        (
            "bytes 42-1233/*",
            ContentRange(range_unit="bytes", first_pos=42, last_pos=1233),
        ),
        ("bytes */1234", ContentRange(range_unit="bytes", complete_length=1234)),
    ],
)
def test_contentrange_from_value(value: str, expected: ContentRange):
    header = ContentRange(value)
    assert header == expected


def test_contentrange_typeerror():
    with pytest.raises(TypeError):
        ContentRange()


@pytest.mark.parametrize(
    "args", [{"range_unit": "bytes", "first_pos": 0}, {"range_unit": "bytes"}]
)
def test_contentrange_valueerror(args: dict[str, Any]):
    with pytest.raises(ValueError):
        ContentRange(**args)
