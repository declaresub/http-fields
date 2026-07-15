from http_headers import EntityTag, ETag


def test_etag_from_value():
    value = 'W/"deadbeef"'
    etag = ETag(value)
    assert etag == ETag(tag="deadbeef", weak=True)


def test_etag_value():
    assert ETag(tag="deadbeef", weak=True).value == 'W/"deadbeef"'


def test_etag_hash():
    assert hash(ETag('"test"'))


def test_etag_matches():
    assert ETag('"test"').matches(EntityTag("test"))
