from http_headers import Expect, Header


def test_expect_parse():
    header = Expect.parse("100-continue")
    assert header.expectations == ("100-continue",)
    assert header.value == "100-continue"


def test_expect_create():
    assert isinstance(Header.create("expect", "100-continue"), Expect)
