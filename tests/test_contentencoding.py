from http_fields import ContentEncoding
from http_fields.visitors.rfc9110 import Token


def test_contentencoding_parse():
    header = ContentEncoding.parse("deflate, gzip")
    assert header.codings == (Token("deflate"), Token("gzip"))


def test_contentencoding_from_codings():
    assert ContentEncoding(Token("deflate"), Token("gzip")).value == "deflate, gzip"


def test_contentencoding_parse_matches_direct():
    assert (
        ContentEncoding.parse("deflate, gzip").codings
        == ContentEncoding(Token("deflate"), Token("gzip")).codings
    )
