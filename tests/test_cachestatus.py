import pytest

from http_headers import CacheStatus, Header, ProxyStatus
from http_headers.structuredfields import Item, Token


def test_cachestatus_parse():
    header = CacheStatus.parse("ExampleCache; hit; ttl=376")
    assert header.members == (
        Item(Token("ExampleCache"), (("hit", True), ("ttl", 376))),
    )
    assert header.value == "ExampleCache;hit;ttl=376"


def test_cachestatus_multiple():
    header = CacheStatus.parse("CacheA; fwd=uri-miss, CacheB; hit")
    assert [m.value for m in header.members if isinstance(m, Item)] == [
        "CacheA",
        "CacheB",
    ]


def test_proxystatus_parse():
    header = ProxyStatus.parse("SomeProxy; error=http_protocol_error")
    assert header.members == (
        Item(Token("SomeProxy"), (("error", Token("http_protocol_error")),)),
    )


def test_cachestatus_create():
    assert isinstance(Header.create("cache-status", "x; hit"), CacheStatus)
    assert isinstance(Header.create("proxy-status", "x"), ProxyStatus)


def test_cachestatus_wrong_member_type_raises_typeerror():
    # A non-Item/InnerList member is a construction-contract error: TypeError
    # (pointing at parse()), not a serializer AssertionError/AttributeError.
    with pytest.raises(TypeError):
        CacheStatus("ExampleCache")  # type: ignore[arg-type]
