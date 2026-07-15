import pytest

from http_headers import ContentEncoding


def test_contenteocoding_from_value():
    content_encoding = ContentEncoding("deflate, gzip")
    print(content_encoding)
    expected = ContentEncoding(["deflate", "gzip"])
    print(expected)
    assert content_encoding.content_coding == expected.content_coding


def test_content_encoding_typeerror():
    with pytest.raises(TypeError):
        ContentEncoding(1)  # type: ignore
