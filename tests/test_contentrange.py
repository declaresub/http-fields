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
        # a first_pos of 0 must not be dropped (falsy-0 regression).
        (
            "bytes 0-99/200",
            ContentRange(
                range_unit="bytes", first_pos=0, last_pos=99, complete_length=200
            ),
        ),
    ],
)
def test_contentrange_parse(value: str, expected: ContentRange):
    assert ContentRange.parse(value) == expected


def test_contentrange_missing_range_unit():
    with pytest.raises(TypeError):
        ContentRange()  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "args", [{"range_unit": "bytes", "first_pos": 0}, {"range_unit": "bytes"}]
)
def test_contentrange_valueerror(args: dict[str, Any]):
    with pytest.raises(ValueError):
        ContentRange(**args)
