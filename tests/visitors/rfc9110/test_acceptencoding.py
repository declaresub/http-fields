import pytest
from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.acceptencoding import (
    AcceptEncodingVisitor,
    WeightedCoding,
)
from http_fields.visitors.rfc9110.weight import Weight


@pytest.mark.parametrize(
    "wc, expected",
    [
        (WeightedCoding("*"), "*"),
        (WeightedCoding("identity", Weight(0.8)), "identity;q=0.8"),
    ],
)
def test_weightedcoding_str(wc: WeightedCoding, expected: str):
    assert str(wc) == expected


def test_acceptencodingvisitor():
    src = "gzip;q=1.0, identity; q=0.5, *;q=0"
    node = rfc9110.Rule("Accept-Encoding").parse_all(src)
    visitor = AcceptEncodingVisitor()
    items = visitor.visit(node)
    expected = [
        WeightedCoding("gzip", 1.0),
        WeightedCoding("identity", 0.5),
        WeightedCoding("*", 0),
    ]
    assert items == expected
