import pytest
from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.weight import Weight, WeightVisitor


@pytest.mark.parametrize(
    "qvalue, expected", [(0.0, "q=0"), (0.5, "q=0.5"), (1.0, "q=1")]
)
def test_weight_str(qvalue: float, expected: str):
    assert str(Weight(qvalue=qvalue)) == expected


def test_weight_visitor_visit():
    src = "; q=0.123"
    node = rfc9110.Rule("weight").parse_all(src)
    visitor = WeightVisitor()
    assert visitor.visit(node) == Weight(qvalue=0.123)
