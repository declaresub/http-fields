from http_headers import EntityTag, ETag


def test_etag_parse():
    assert ETag.parse('W/"deadbeef"') == ETag.from_tag("deadbeef", weak=True)


def test_etag_value():
    assert ETag.from_tag("deadbeef", weak=True).value == 'W/"deadbeef"'


def test_etag_hash():
    assert hash(ETag.parse('"test"'))


def test_etag_matches():
    assert ETag.parse('"test"').matches(EntityTag("test"))
