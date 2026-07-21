from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from http_headers.setcookie import SetCookie, parse_cookie_date


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "Wed, 09 Jun 2021 10:18:14 GMT",
            datetime(2021, 6, 9, 10, 18, 14, tzinfo=timezone.utc),
        ),
        (
            "Sat, 30-Jul-2022 05:12:54 GMT",
            datetime(2022, 7, 30, 5, 12, 54, tzinfo=timezone.utc),
        ),  # some sort of PHP generated format, from https://github.com/php/php-src/issues/9200
        (
            "Fri, 31 Dec 99 10:18:14 GMT",
            datetime(1999, 12, 31, 10, 18, 14, tzinfo=timezone.utc),
        ),
        (
            "Wed, 09 Jun 21 10:18:14 GMT",
            datetime(2021, 6, 9, 10, 18, 14, tzinfo=timezone.utc),
        ),
    ],
)
def test_parse_cookie_date(value: str, expected: datetime):
    assert parse_cookie_date(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "Sat 30-Jul-2022",
        "Wed, Jun 2021 10:18:14 GMT",
        "Wed, 09  2021 10:18:14 GMT",
        "Wed, 09 Jun  10:18:14 GMT",
        "Wed, 33 Jun 2021 10:18:14 GMT",
        "Sun, 31 Dec 1600 10:18:14 GMT",
    ],
)
def test_parse_bad_cookie_date(value: str):
    with pytest.raises(ValueError):
        parse_cookie_date(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        # Times with zero-valued fields must not be dropped (regression: bug 1).
        (
            "Wed, 09 Jun 2021 10:00:05 GMT",
            datetime(2021, 6, 9, 10, 0, 5, tzinfo=timezone.utc),
        ),
        (
            "Wed, 09 Jun 2021 00:00:00 GMT",
            datetime(2021, 6, 9, 0, 0, 0, tzinfo=timezone.utc),
        ),
        (
            "Wed, 09 Jun 2021 16:00:00 GMT",
            datetime(2021, 6, 9, 16, 0, 0, tzinfo=timezone.utc),
        ),
    ],
)
def test_parse_cookie_date_zero_fields(value: str, expected: datetime):
    assert parse_cookie_date(value) == expected


def test_parse_setcookie_expires_on_the_hour():
    cookie = SetCookie.parse("a=b; Expires=Wed, 09 Jun 2021 10:00:05 GMT")
    assert cookie.expires == datetime(2021, 6, 9, 10, 0, 5, tzinfo=timezone.utc)


@pytest.mark.parametrize("value", ["foo", "=b", "  "])
def test_parse_setcookie_missing_name_rejected(value: str):
    # RFC 6265 section 5.2: a name-value pair without "=", or with an empty
    # name, must be ignored entirely (regression: bug 2).
    with pytest.raises(ValueError):
        SetCookie.parse(value)


def test_parse_setcookie_empty_domain_and_path():
    # Empty Domain=/Path= attribute values must not crash (regression: bug 2).
    assert SetCookie.parse("a=b; Domain=").domain is None
    assert SetCookie.parse("a=b; Path=").path is None


def test_parse_setcookie_preserves_bracket():
    # The strip set must not include "]" (regression: bug 10).
    assert SetCookie.parse("a=[v]").cookie_value == "[v]"
    assert SetCookie.parse("a=b]; Path=/x]").cookie_value == "b]"


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "SID=31d4d96e407aad42",
            SetCookie.build(cookie_name="SID", cookie_value="31d4d96e407aad42"),
        ),
        (
            "SID=31d4d96e407aad42; Path=/; Domain=example.com",
            SetCookie.build(
                cookie_name="SID",
                cookie_value="31d4d96e407aad42",
                path="/",
                domain="example.com",
            ),
        ),
        (
            "SID=31d4d96e407aad42; Path=/; Secure; HttpOnly",
            SetCookie.build(
                cookie_name="SID",
                cookie_value="31d4d96e407aad42",
                path="/",
                secure=True,
                http_only=True,
            ),
        ),
        (
            "lang=en-US; Expires=Wed, 09 Jun 2021 10:18:14 GMT",
            SetCookie.build(
                cookie_name="lang",
                cookie_value="en-US",
                expires=datetime(2021, 6, 9, 10, 18, 14, tzinfo=timezone.utc),
            ),
        ),
    ],
)
def test_setcookie_from_value(value: str, expected: SetCookie):
    assert SetCookie.parse(value) == expected


@pytest.mark.parametrize(
    "header",
    [
        SetCookie.build(cookie_name="SID", cookie_value="31d4d96e407aad42", max_age=43),
        SetCookie.build(
            cookie_name="SID",
            cookie_value="31d4d96e407aad42",
            path="/",
            domain="example.com",
            secure=True,
            http_only=True,
            expires=datetime(2021, 6, 9, 10, 18, 14, tzinfo=timezone.utc),
        ),
        SetCookie.build(
            cookie_name="SID", cookie_value="31d4d96e407aad42", extension=["test"]
        ),
    ],
)
def test_setcookie_from_init(header: SetCookie):
    assert SetCookie.parse(header.value) == header


@pytest.mark.parametrize(
    "cookie_name, cookie_value",
    [
        (b"foo", "bar"),
        ("foo", b"bar"),
    ],
)
def test_bad_arg_type(cookie_name: Any, cookie_value: Any):
    with pytest.raises(TypeError):
        SetCookie.build(cookie_name=cookie_name, cookie_value=cookie_value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"cookie_name": "foo,", "cookie_value": "bar"},
        {"cookie_name": "foo", "cookie_value": "bar,"},
        {"cookie_name": "foo", "cookie_value": "bar", "domain": "example..com"},
        {"cookie_name": "foo", "cookie_value": "bar", "path": "/foo;"},
        {
            "cookie_name": "foo",
            "cookie_value": "bar",
            "expires": datetime(1600, 12, 31),
        },
    ],
)
def test_bad_arg_value(kwargs: dict[str, Any]):
    with pytest.raises(ValueError):
        SetCookie.build(**kwargs)


@pytest.mark.parametrize(
    "request_path, expected",
    [
        ("", "/"),
        ("/", "/"),
        ("/foo", "/"),
        ("/foo/", "/foo"),
        ("/foo/bar", "/foo"),
        ("relative/path", "/"),
    ],
)
def test_default_path(request_path: str, expected: str):
    assert SetCookie.default_path(request_path) == expected


@pytest.mark.parametrize(
    "src",
    [
        "foo=bar\ntest=test",
    ],
)
def test_bad_src(src: str):
    with pytest.raises(ValueError):
        SetCookie.parse(src)


def test_invalid_expires():
    header = SetCookie.parse(
        "SID=31d4d96e407aad42; Expires=Fri, 09 Jun 1600 10:18:14 GMT"
    )
    assert header.expires is None


def test_invalid_max_age():
    header = SetCookie.parse("SID=31d4d96e407aad42; Max-Age=x")
    assert header.max_age is None


def test_expiry_time1():
    now = datetime.now(timezone.utc)
    header = SetCookie.build(cookie_name="name", cookie_value="value", max_age=100)
    assert header.expiry_time(now=now) == now + timedelta(seconds=100)


def test_expiry_time2():
    header = SetCookie.build(cookie_name="name", cookie_value="value", max_age=100)
    assert header.expiry_time()


def test_expiry_time3():
    header = SetCookie.build(cookie_name="name", cookie_value="value", max_age=0)
    assert header.expiry_time() == datetime.fromtimestamp(0, timezone.utc)


def test_expiry_time4():
    expires = datetime(2022, 4, 1, tzinfo=timezone.utc)
    header = SetCookie.build(cookie_name="name", cookie_value="value", expires=expires)
    assert header.expiry_time() == expires


def test_expiry_time5():
    header = SetCookie.build(cookie_name="name", cookie_value="value")
    assert header.expiry_time() is None


def test_setcookie_no_samesite_not_invented():
    # parse -> serialize must not add a SameSite the origin never set (bug 18).
    assert SetCookie.parse("a=b").value == "a=b"


def test_setcookie_samesite_preserved():
    assert SetCookie.parse("a=b; SameSite=Strict").value == "a=b; SameSite=Strict"


def test_setcookie_unknown_samesite_not_default():
    # an unrecognized SameSite must never serialize as the invalid "SameSite=Default".
    cookie = SetCookie.parse("a=b; SameSite=weird")
    assert "Default" not in cookie.value


def test_setcookie_samesite_none_does_not_invent_secure():
    # SameSite=None must not fabricate a Secure attribute; the round-trip and
    # secure flag must be preserved (regression: round 2, bug 1).
    cookie = SetCookie.parse("a=b; SameSite=None")
    assert cookie.secure is False
    assert cookie.value == "a=b; SameSite=None"
    assert SetCookie.parse(cookie.value) == cookie


def test_setcookie_samesite_none_keeps_explicit_secure():
    cookie = SetCookie.parse("a=b; SameSite=None; Secure")
    assert cookie.secure is True
    assert SetCookie.parse(cookie.value) == cookie


@pytest.mark.parametrize("bad_extension", [["bad\r\nx"], ["a=b=c;d"], ["", "ok"]])
def test_setcookie_build_bad_extension_raises_valueerror(bad_extension: list[str]):
    # build() must raise ValueError (its documented failure mode), not the raw
    # abnf ParseError, for an invalid extension-av (round 2, bug 3 / security low).
    with pytest.raises(ValueError):
        SetCookie.build(cookie_name="n", cookie_value="v", extension=bad_extension)
