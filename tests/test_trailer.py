from http_headers import Header, Trailer


def test_trailer_parse():
    header = Trailer.parse("Expires, Content-MD5")
    assert header.field_names == ("Expires", "Content-MD5")


def test_trailer_value():
    assert Trailer("Expires", "Content-MD5").value == "Expires, Content-MD5"


def test_trailer_create():
    assert isinstance(Header.create("trailer", "Expires"), Trailer)
