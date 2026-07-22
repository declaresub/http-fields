from http_fields import AcceptCharset


def test_acceptcharset_parse():
    assert AcceptCharset.parse("*; q=0.5") == AcceptCharset(("*", 0.5))


def test_acceptcharset_value():
    assert AcceptCharset(("*", 0.5)).value == "*;q=0.5"


def test_acceptcharset_no_weight():
    # a charset with no weight must still be serialized (falsy-weight regression).
    assert AcceptCharset(("utf-8", None)).value == "utf-8"
