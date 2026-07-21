"""Property test: for every header, ``parse(h.value) == h``.

Serializing a parsed header and parsing the result must reproduce an equal object.
This guards against the "serializer emits unparseable / lossy output" class of bug
(review findings 4, 6, 12, 14, 18, 23). The coverage test at the bottom fails if a
new concrete Header subclass is added without a sample here.
"""

import inspect

import pytest

import http_headers as hh
from http_headers.header import Header

# One representative, valid raw value per concrete header class.
SAMPLES: dict[str, str] = {
    "Accept": "text/html, application/json;q=0.8",
    "AcceptCharset": "utf-8, iso-8859-1;q=0.5",
    "AcceptEncoding": "gzip, deflate;q=0.5",
    "AcceptLanguage": "en-US, en;q=0.9",
    "AcceptRanges": "bytes",
    "AccessControlAllowCredentials": "true",
    "AccessControlAllowHeaders": "X-Custom, Content-Type",
    "AccessControlAllowMethods": "GET, POST",
    "AccessControlAllowOrigin": "https://example.com",
    "AccessControlExposeHeaders": "X-Custom",
    "AccessControlMaxAge": "600",
    "AccessControlRequestHeaders": "X-Custom",
    "AccessControlRequestMethod": "GET",
    "Age": "60",
    "Allow": "GET, POST, OPTIONS",
    "AltSvc": "clear",
    "AltUsed": "example.com:443",
    "AuthenticationInfo": 'nextnonce="abc123"',
    "Authorization": "Basic dGVzdDp0ZXN0",
    "CacheControl": "max-age=3600, no-cache",
    "CacheStatus": "ExampleCache; hit; ttl=376",
    "Connection": "keep-alive",
    "ContentDigest": "sha-256=:AA==:",
    "ContentDisposition": 'attachment; filename="f.txt"',
    "ContentEncoding": "gzip",
    "ContentLanguage": "en-US",
    "ContentLength": "1234",
    "ContentLocation": "/index.html",
    "ContentRange": "bytes 0-499/1234",
    "ContentType": "text/html; charset=utf-8",
    "Cookie": "a=b; c=d",
    "Date": "Sun, 06 Nov 1994 08:49:37 GMT",
    "ETag": '"deadbeef"',
    "Expect": "100-continue",
    "Expires": "Sun, 06 Nov 1994 08:49:37 GMT",
    "Forwarded": "for=192.0.2.60;proto=http;by=203.0.113.43",
    "From": "test@example.com",
    "Host": "example.com:8080",
    "IfMatch": '"tag"',
    "IfModifiedSince": "Sun, 06 Nov 1994 08:49:37 GMT",
    "IfNoneMatch": '"tag"',
    "IfRange": '"tag"',
    "IfUnmodifiedSince": "Sun, 06 Nov 1994 08:49:37 GMT",
    "LastModified": "Sun, 06 Nov 1994 08:49:37 GMT",
    "Link": '<https://example.com>; rel="next"',
    "Location": "https://example.com/path",
    "MaxForwards": "10",
    "Origin": "https://example.com",
    "Prefer": "respond-async",
    "PreferenceApplied": "respond-async",
    "Priority": "u=5, i",
    "ProxyAuthenticate": 'Basic realm="test"',
    "ProxyAuthenticationInfo": 'nextnonce="abc123"',
    "ProxyAuthorization": "Basic dGVzdDp0ZXN0",
    "ProxyStatus": "ExampleProxy",
    "Range": "bytes=0-499, -300",
    "Referer": "https://example.com/",
    "ReprDigest": "sha-256=:AA==:",
    "RetryAfter": "120",
    "Server": "Apache/2.4.1",
    "SetCookie": "SID=abc123; Path=/; Secure",
    "StrictTransportSecurity": "max-age=31536000; includeSubDomains",
    "TE": "trailers, deflate;q=0.5",
    "Trailer": "Expires",
    "Upgrade": "websocket",
    "UserAgent": "Mozilla/5.0 (Windows NT 10.0) Gecko/20100101",
    "Vary": "Accept-Encoding, User-Agent",
    "Via": "1.1 vegur",
    "WWWAuthenticate": 'Basic realm="test"',
}


@pytest.mark.parametrize("clsname, value", sorted(SAMPLES.items()))
def test_roundtrip(clsname: str, value: str):
    cls = getattr(hh, clsname)
    header = cls.parse(value)
    # parse(h.value) == h
    assert cls.parse(header.value) == header
    # serialization is idempotent
    assert cls.parse(header.value).value == header.value


def _concrete_header_names() -> set[str]:
    names: set[str] = set()
    for name in hh.__all__:
        obj = getattr(hh, name)
        if (
            inspect.isclass(obj)
            and issubclass(obj, Header)
            and obj is not Header
            and isinstance(getattr(obj, "name", None), str)
        ):
            names.add(name)
    return names


def test_every_header_has_a_roundtrip_sample():
    # A new concrete header must be added to SAMPLES so it is round-trip tested.
    missing = _concrete_header_names() - set(SAMPLES)
    assert not missing, f"headers without a round-trip sample: {sorted(missing)}"
