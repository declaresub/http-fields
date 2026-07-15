import pytest

from http_headers import Cookie


@pytest.mark.parametrize(
    "value, expected",
    [
        ("a=b; c=d", Cookie([("a", "b"), ("c", "d")])),
    ],
)
def test_cookie_from_value(value: str, expected: Cookie):
    cookie = Cookie(value)
    assert cookie.pairs == expected.pairs


def test_cookie_value():
    value = "foo=bar"
    cookie = Cookie(value)
    assert cookie.value == value


def test_cookie_bad_args():
    with pytest.raises(TypeError):
        Cookie(("foo", "bar"))  # type: ignore
