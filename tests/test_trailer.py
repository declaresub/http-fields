from http_fields import Header, Trailer
from http_fields.visitors.rfc9110 import FieldName


def test_trailer_parse():
    header = Trailer.parse("Expires, Content-MD5")
    assert header.field_names == ("Expires", "Content-MD5")


def test_trailer_value():
    assert (
        Trailer(FieldName("Expires"), FieldName("Content-MD5")).value
        == "Expires, Content-MD5"
    )


def test_trailer_create():
    assert isinstance(Header.create("trailer", "Expires"), Trailer)
