import pytest

from http_headers import ContentType
from http_headers.visitors.rfc9110 import Parameter


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "text/html; charset=UTF-8",
            ContentType.of(type="text", subtype="html", charset="utf-8"),
        ),
        (
            "multipart/form-data; boundary=something",
            ContentType.of(type="multipart", subtype="form-data", boundary="something"),
        ),
    ],
)
def test_contenttype_parse(value: str, expected: ContentType):
    assert ContentType.parse(value) == expected


def test_contenttype_params():
    header = ContentType.of(type="test", subtype="test", params=[("foo", "bar")])
    assert header.params == [Parameter("foo", "bar")]


def test_contenttype_type_subtype():
    header = ContentType.of(type="test", subtype="test")
    assert header.type == "test"
    assert header.subtype == "test"


@pytest.mark.parametrize(
    "header, expected",
    [
        (ContentType.of(type="text", subtype="html", charset="utf-8"), "utf-8"),
        (ContentType.of(type="text", subtype="html"), None),
        (
            ContentType.of(
                type="text",
                subtype="html",
                charset="utf-7",
                params=[("charset", "utf-8")],
            ),
            "utf-7",
        ),
    ],
)
def test_contenttype_charset(header: ContentType, expected: str | None):
    assert header.charset == expected


@pytest.mark.parametrize(
    "header, expected",
    [
        (
            ContentType.of(type="multipart", subtype="form-data", boundary="test"),
            "test",
        ),
        (
            ContentType.of(
                type="multipart",
                subtype="form-data",
                boundary="test",
                params=[("boundary", "foo")],
            ),
            "test",
        ),
        (ContentType.of(type="text", subtype="html"), None),
    ],
)
def test_contenttype_boundary(header: ContentType, expected: str | None):
    assert header.boundary == expected


def test_contenttype_value():
    assert (
        ContentType.of(type="text", subtype="html", charset="utf-8").value
        == "text/html;charset=utf-8"
    )


def test_contenttype_missing_type():
    with pytest.raises(TypeError):
        ContentType.of()  # type: ignore[call-arg]


def test_contenttype_missing_subtype():
    with pytest.raises(TypeError):
        ContentType.of(type="text")  # type: ignore[call-arg]


def test_contenttype_eq():
    assert ContentType.of(
        type="text", subtype="html", charset="utf-8"
    ) == ContentType.of(type="text", subtype="html", charset="utf-8")
