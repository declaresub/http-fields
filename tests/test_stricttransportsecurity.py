import pytest

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


def test_hsts_quoted_max_age():
    # RFC 6797 section 6.1 allows a quoted-string directive-value (regression: bug 16).
    header = StrictTransportSecurity.parse('max-age="600"')
    assert header.max_age == 600


def test_hsts_missing_max_age_rejected():
    # An STS header without max-age must be ignored/rejected, not treated as
    # max-age=0 (which would delete the policy).
    with pytest.raises(ValueError):
        StrictTransportSecurity.parse("preload")
    with pytest.raises(ValueError):
        StrictTransportSecurity.parse("includeSubDomains")
