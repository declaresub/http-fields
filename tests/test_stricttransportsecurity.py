from http_headers import Header, StrictTransportSecurity


def test_hsts_parse():
    header = StrictTransportSecurity.parse("max-age=31536000; includeSubDomains")
    assert header.max_age == 31536000
    assert header.include_subdomains is True
    assert header.preload is False


def test_hsts_value():
    header = StrictTransportSecurity(31536000, include_subdomains=True, preload=True)
    assert header.value == "max-age=31536000; includeSubDomains; preload"


def test_hsts_roundtrip():
    assert StrictTransportSecurity.parse("max-age=600").value == "max-age=600"


def test_hsts_create():
    assert isinstance(
        Header.create("strict-transport-security", "max-age=0"),
        StrictTransportSecurity,
    )
