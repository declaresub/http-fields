"""Security: no construction path may smuggle CR/LF/NUL into a header value.

The natural constructors (not just parse()) must validate their string inputs, so
an application that builds a header from partially-attacker-controlled data cannot
be tricked into response splitting / header injection.
"""

import pytest

from http_fields import (
    AcceptRanges,
    AccessControlAllowHeaders,
    AccessControlAllowMethods,
    AccessControlAllowOrigin,
    AccessControlExposeHeaders,
    AccessControlRequestHeaders,
    AccessControlRequestMethod,
    Allow,
    Connection,
    ContentEncoding,
    ContentLanguage,
    ContentLocation,
    Expect,
    Host,
    Location,
    Origin,
    Referer,
    SetCookie,
    Trailer,
    Vary,
)
from http_fields.accesscontrol import CorsFieldName, CorsMethod
from http_fields.allow import Method
from http_fields.visitors.rfc9110 import FieldName, RangeUnit, Token
from http_fields.visitors.rfc9110.contentlanguage import LanguageTag

# CRLF (response splitting), bare LF, and NUL.
BAD = ["x\r\nSet-Cookie: p=1", "x\nY: z", "x\x00y"]

# Scalar-string headers that still accept a raw string, validated in __init__.
STRING_CONSTRUCTORS = [
    Location,
    Referer,
    ContentLocation,
    Origin,
    AccessControlAllowOrigin,
    AccessControlRequestMethod,
    Host,
]


@pytest.mark.parametrize("ctor", STRING_CONSTRUCTORS, ids=lambda c: c.__name__)
@pytest.mark.parametrize("bad", BAD)
def test_string_constructor_rejects_injection(ctor, bad):
    with pytest.raises(ValueError):
        ctor(bad)


# Strict list headers take leaf types, so an untrusted string goes through parse()
# (which validates); passing a raw string to the constructor is a TypeError instead.
STRICT_LIST_HEADERS = [
    Connection,
    Allow,
    Vary,
    Trailer,
    AcceptRanges,
    ContentEncoding,
    ContentLanguage,
    AccessControlAllowMethods,
    AccessControlAllowHeaders,
    AccessControlExposeHeaders,
    AccessControlRequestHeaders,
]


@pytest.mark.parametrize("ctor", STRICT_LIST_HEADERS, ids=lambda c: c.__name__)
@pytest.mark.parametrize("bad", BAD)
def test_strict_list_parse_rejects_injection(ctor, bad):
    with pytest.raises(ValueError):
        ctor.parse(bad)


# The leaf types that those headers are built from must reject injection at
# construction, so a value object can never hold a control character.
LEAF_TYPES = [
    Token,
    Method,
    FieldName,
    RangeUnit,
    LanguageTag,
    CorsMethod,
    CorsFieldName,
]


@pytest.mark.parametrize("leaf", LEAF_TYPES, ids=lambda t: t.__name__)
@pytest.mark.parametrize("bad", BAD)
def test_leaf_type_rejects_injection(leaf, bad):
    with pytest.raises(ValueError):
        leaf(bad)


@pytest.mark.parametrize("bad", BAD)
def test_expect_strict_contract(bad):
    # Strict, typed construction: untrusted strings go through parse() (which
    # validates), and the constructor takes already-parsed Expectation values.
    from http_fields.expect import Expectation

    with pytest.raises(ValueError):
        Expect.parse(bad)
    with pytest.raises(TypeError):
        Expect(bad)  # type: ignore[arg-type]  # str is not an Expectation
    assert Expect(Expectation("100-continue")).value == "100-continue"


@pytest.mark.parametrize("bad", BAD)
def test_setcookie_constructor_rejects_injection(bad):
    with pytest.raises(ValueError):
        SetCookie(cookie_name="a", cookie_value=bad)
    with pytest.raises(ValueError):
        SetCookie(cookie_name=bad, cookie_value="b")


# Headers that hold value-objects: a bad string inside a value-object must be
# rejected when the header is constructed (validated at the header's __init__).
def _value_object_headers(bad):
    from http_fields import (
        TE,
        AltSvc,
        AltUsed,
        CacheControl,
        CacheStatus,
        ContentDigest,
        Forwarded,
        From,
        Link,
        Prefer,
        PreferenceApplied,
        ProxyStatus,
        ReprDigest,
        Upgrade,
        Via,
    )
    from http_fields.structuredfields import Item
    from http_fields.visitors.rfc7239 import ForwardedElement
    from http_fields.visitors.rfc7240 import Preference
    from http_fields.visitors.rfc7838 import AltValue
    from http_fields.visitors.rfc8288 import LinkValue
    from http_fields.visitors.rfc9110.te import TCoding
    from http_fields.visitors.rfc9110.upgrade import Protocol
    from http_fields.visitors.rfc9110.via import ViaElement

    return [
        ("AltUsed", lambda: AltUsed(bad)),
        ("From", lambda: From(bad)),
        ("ContentDigest", lambda: ContentDigest((bad, b"x"))),
        ("ReprDigest", lambda: ReprDigest((bad, b"x"))),
        ("CacheControl.no_cache", lambda: CacheControl(no_cache=bad)),
        ("CacheControl.private", lambda: CacheControl(private=bad)),
        ("AltSvc", lambda: AltSvc(AltValue(bad, "example.com:443"))),
        ("Forwarded", lambda: Forwarded(ForwardedElement(((bad, "v"),)))),
        ("Link", lambda: Link(LinkValue(bad))),
        ("Via", lambda: Via(ViaElement(bad, "host"))),
        ("Prefer", lambda: Prefer(Preference(bad))),
        ("PreferenceApplied", lambda: PreferenceApplied(Preference(bad))),
        ("TE", lambda: TE(TCoding(bad))),
        ("Upgrade", lambda: Upgrade(Protocol(bad))),
        ("CacheStatus", lambda: CacheStatus(Item(bad))),
        ("ProxyStatus", lambda: ProxyStatus(Item(bad))),
    ]


@pytest.mark.parametrize("bad", BAD)
def test_value_object_headers_reject_injection(bad):
    for label, ctor in _value_object_headers(bad):
        try:
            ctor()
        except ValueError:
            continue
        pytest.fail(f"{label} did not reject injection of {bad!r}")
