from http_headers import Header, IntRange, Range, SuffixRange


def test_range_parse():
    header = Range.parse("bytes=0-499, 500-, -300")
    assert header.range_unit == "bytes"
    assert header.ranges == (
        IntRange(0, 499),
        IntRange(500, None),
        SuffixRange(300),
    )


def test_range_value():
    header = Range("bytes", IntRange(0, 499), SuffixRange(300))
    assert header.value == "bytes=0-499,-300"


def test_range_roundtrip():
    assert Range.parse("bytes=0-499,-300").value == "bytes=0-499,-300"


def test_range_create():
    assert isinstance(Header.create("range", "bytes=0-"), Range)
