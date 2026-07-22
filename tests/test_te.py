from http_fields import TE, Header, TCoding


def test_te_parse():
    header = TE.parse("gzip;q=0.5, trailers")
    assert [c.coding for c in header.codings] == ["gzip", "trailers"]
    assert str(header.codings[0].weight) == "q=0.5"
    assert header.codings[1].weight is None


def test_te_roundtrip():
    assert TE.parse("gzip;q=0.5, trailers").value == "gzip;q=0.5, trailers"


def test_te_value_from_codings():
    assert TE(TCoding("trailers")).value == "trailers"


def test_te_create():
    assert isinstance(Header.create("te", "trailers"), TE)
