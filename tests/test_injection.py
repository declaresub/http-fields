"""Security: no construction path may smuggle CR/LF/NUL into a header value.

The natural constructors (not just parse()) must validate their string inputs, so
an application that builds a header from partially-attacker-controlled data cannot
be tricked into response splitting / header injection.
"""

import pytest

from http_headers import (
    AccessControlAllowHeaders,
    AccessControlAllowMethods,
    AccessControlAllowOrigin,
    AccessControlExposeHeaders,
    AccessControlRequestHeaders,
    AccessControlRequestMethod,
    ContentLocation,
    Expect,
    Host,
    Location,
    Origin,
    Referer,
    SetCookie,
)

# CRLF (response splitting), bare LF, and NUL.
BAD = ["x\r\nSet-Cookie: p=1", "x\nY: z", "x\x00y"]

CONSTRUCTORS = [
    Location,
    Referer,
    ContentLocation,
    Origin,
    AccessControlAllowOrigin,
    AccessControlRequestMethod,
    AccessControlAllowMethods,
    AccessControlAllowHeaders,
    AccessControlExposeHeaders,
    AccessControlRequestHeaders,
    Host,
    Expect,
]


@pytest.mark.parametrize("ctor", CONSTRUCTORS, ids=lambda c: c.__name__)
@pytest.mark.parametrize("bad", BAD)
def test_constructor_rejects_injection(ctor, bad):
    with pytest.raises(ValueError):
        ctor(bad)


@pytest.mark.parametrize("bad", BAD)
def test_setcookie_constructor_rejects_injection(bad):
    with pytest.raises(ValueError):
        SetCookie(cookie_name="a", cookie_value=bad)
    with pytest.raises(ValueError):
        SetCookie(cookie_name=bad, cookie_value="b")
