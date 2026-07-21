from dataclasses import FrozenInstanceError

import pytest

from http_headers import EntityTag, ETag


def test_entitytag_is_frozen():
    et = EntityTag("abc")
    with pytest.raises(FrozenInstanceError):
        et.weak = True  # type: ignore[misc]
    assert et == EntityTag("abc")
    assert repr(et) == "EntityTag(opaque_tag='\"abc\"', weak=False)"


def test_etag_parse():
    assert ETag.parse('W/"deadbeef"') == ETag.from_tag("deadbeef", weak=True)


def test_etag_value():
    assert ETag.from_tag("deadbeef", weak=True).value == 'W/"deadbeef"'


def test_etag_hash():
    assert hash(ETag.parse('"test"'))


def test_etag_matches():
    assert ETag.parse('"test"').matches(EntityTag("test"))


def test_etag_empty_strong():
    # An empty opaque-tag is grammar-valid (regression: bug 7).
    etag = ETag.parse('""')
    assert etag.value == '""'
    assert etag == ETag.from_tag("", weak=False)


def test_etag_empty_weak():
    etag = ETag.parse('W/""')
    assert etag.value == 'W/""'
    assert etag == ETag.from_tag("", weak=True)
