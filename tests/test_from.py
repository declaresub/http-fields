import pytest

from http_headers import From, Header


def test_from_parse():
    header = From.parse("webmaster@example.org")
    assert header.mailbox == "webmaster@example.org"
    assert header.value == "webmaster@example.org"


def test_from_invalid():
    with pytest.raises(ValueError):
        From.parse("not a mailbox")


def test_from_create():
    assert isinstance(Header.create("from", "a@b.com"), From)
