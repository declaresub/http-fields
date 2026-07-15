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
        (
            "SID=31d4d96e407aad42",
            SetCookie(cookie_name="SID", cookie_value="31d4d96e407aad42"),
        ),
        (
            "SID=31d4d96e407aad42; Path=/; Domain=example.com",
            SetCookie(
                cookie_name="SID",
                cookie_value="31d4d96e407aad42",
                path="/",
                domain="example.com",
            ),
        ),
        (
            "SID=31d4d96e407aad42; Path=/; Secure; HttpOnly",
            SetCookie(
                cookie_name="SID",
                cookie_value="31d4d96e407aad42",
                path="/",
                secure=True,
                http_only=True,
            ),
        ),
        (
            "lang=en-US; Expires=Wed, 09 Jun 2021 10:18:14 GMT",
            SetCookie(
                cookie_name="lang",
                cookie_value="en-US",
                expires=datetime(2021, 6, 9, 10, 18, 14, tzinfo=timezone.utc),
            ),
        ),
    ],
)
def test_setcookie_from_value(value: str, expected: SetCookie):
    assert SetCookie(value) == expected


@pytest.mark.parametrize(
    "header",
    [
        SetCookie(cookie_name="SID", cookie_value="31d4d96e407aad42", max_age=43),
        SetCookie(
            cookie_name="SID",
            cookie_value="31d4d96e407aad42",
            path="/",
            domain="example.com",
            secure=True,
            http_only=True,
            expires=datetime(2021, 6, 9, 10, 18, 14, tzinfo=timezone.utc),
        ),
        SetCookie(
            cookie_name="SID", cookie_value="31d4d96e407aad42", extension=["test"]
        ),
    ],
)
def test_setcookie_from_init(header: SetCookie):
    assert SetCookie(header.value) == header


@pytest.mark.parametrize(
    "cookie_name, cookie_value",
    [
        (b"foo", "bar"),
        ("foo", b"bar"),
    ],
)
def test_bad_arg_type(cookie_name: Any, cookie_value: Any):
    with pytest.raises(TypeError):
        SetCookie(cookie_name=cookie_name, cookie_value=cookie_value)


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
        SetCookie(**kwargs)


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
        # f'name={"value"*2048}', test case for RFC 6265bis
        # f'name=value; path=/{"x"*1025}', test case for RFC 6265bis
    ],
)
def test_bad_src(src: str):
    with pytest.raises(ValueError):
        SetCookie(src)


def test_invalid_expires():
    header = SetCookie("SID=31d4d96e407aad42; Expires=Fri, 09 Jun 1600 10:18:14 GMT")
    assert header.expires is None


def test_invalid_max_age():
    header = SetCookie("SID=31d4d96e407aad42; Max-Age=x")
    assert header.max_age is None


def test_expiry_time1():
    now = datetime.now(timezone.utc)
    header = SetCookie(cookie_name="name", cookie_value="value", max_age=100)
    assert header.expiry_time(now=now) == now + timedelta(seconds=100)


def test_expiry_time2():
    header = SetCookie(cookie_name="name", cookie_value="value", max_age=100)
    assert header.expiry_time()


def test_expiry_time3():
    header = SetCookie(cookie_name="name", cookie_value="value", max_age=0)
    assert header.expiry_time() == datetime.fromtimestamp(0, timezone.utc)


def test_expiry_time4():
    expires = datetime(2022, 4, 1, tzinfo=timezone.utc)
    header = SetCookie(cookie_name="name", cookie_value="value", expires=expires)
    assert header.expiry_time() == expires


def test_expiry_time5():
    header = SetCookie(cookie_name="name", cookie_value="value")
    assert header.expiry_time() is None
