import pytest

from http_headers import ContentType
from http_headers.visitors.rfc9110 import Parameter


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "text/html; charset=UTF-8",
            ContentType(type="text", subtype="html", charset="utf-8"),
        ),
        (
            "multipart/form-data; boundary=something",
            ContentType(type="multipart", subtype="form-data", boundary="something"),
        ),
    ],
)
def test_contenttype_from_value(value: str, expected: ContentType):
    print(ContentType(value))
    print(expected)
    assert ContentType(value) == expected


def test_contenttype_params():
    header = ContentType(type="test", subtype="test", params=[("foo", "bar")])
    assert header.params == [Parameter("foo", "bar")]


def test_content_type_type():
    header = ContentType(type="test", subtype="test")
    assert header.type == "test"
    assert header.subtype == "test"


@pytest.mark.parametrize(
    "header, expected",
    [
        (ContentType(type="text", subtype="html", charset="utf-8"), "utf-8"),
        (ContentType(type="text", subtype="html"), None),
        (
            ContentType(
                type="text",
                subtype="html",
                charset="utf-7",
                params=[("charset", "utf-8")],
            ),
            "utf-7",
        ),
    ],
)
def test_content_type_charset(header: ContentType, expected: str | None):
    assert header.charset == expected


@pytest.mark.parametrize(
    "header, expected",
    [
        (ContentType(type="multipart", subtype="form-data", boundary="test"), "test"),
        (
            ContentType(
                type="multipart",
                subtype="form-data",
                boundary="test",
                params=[("boundary", "foo")],
            ),
            "test",
        ),
        (ContentType(type="text", subtype="html"), None),
    ],
)
def test_contenttype_boundary(header: ContentType, expected: str | None):
    assert header.boundary == expected


def test_contenttype_value():
    assert (
        ContentType(type="text", subtype="html", charset="utf-8").value
        == "text/html;charset=utf-8"
    )


def test_content_type_missing_type():
    with pytest.raises(TypeError):
        ContentType()


def test_content_type_missing_subtype():
    with pytest.raises(TypeError):
        ContentType(type="text")


def test_contenttype_eq():
    assert ContentType(type="text", subtype="html", charset="utf-8") == ContentType(
        type="text", subtype="html", charset="utf-8"
    )
