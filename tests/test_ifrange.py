from datetime import datetime, timezone

import pytest

from http_fields import EntityTag, Header, IfRange


def test_ifrange_parse_etag():
    header = IfRange.parse('W/"abc"')
    assert header.condition == EntityTag("abc", weak=True)
    assert header.value == 'W/"abc"'


def test_ifrange_parse_date():
    header = IfRange.parse("Wed, 21 Oct 2015 07:28:00 GMT")
    assert header.condition == datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc)


def test_ifrange_from_datetime():
    dt = datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc)
    assert IfRange(dt).value == "Wed, 21 Oct 2015 07:28:00 GMT"


def test_ifrange_bad_type():
    with pytest.raises(TypeError):
        IfRange("nope")  # type: ignore[arg-type]


def test_ifrange_create():
    assert isinstance(Header.create("if-range", '"x"'), IfRange)
