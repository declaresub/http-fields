import pytest

from http_headers import AcceptRanges, RangeUnit


@pytest.mark.parametrize(
    "value, expected",
    [
        (["bytes"], (RangeUnit("bytes"),)),
        (["bytes", "blobs"], (RangeUnit("bytes"), RangeUnit("blobs"))),
    ],
)
def test_acceptranges(value: list[str], expected: tuple[RangeUnit, ...]):
    header = AcceptRanges(*(RangeUnit(v) for v in value))
    assert header.range_units == expected


def test_acceptranges_value():
    header = AcceptRanges(RangeUnit("bytes"), RangeUnit("blobs"))
    assert header.value == "bytes,blobs"


def test_acceptranges_parse_bad():
    with pytest.raises(ValueError):
        AcceptRanges(RangeUnit("bytes\r\nblobs"))
