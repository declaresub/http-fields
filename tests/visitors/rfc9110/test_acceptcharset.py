from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.acceptcharset import AcceptCharsetVisitor
from http_headers.visitors.rfc9110.token import Token
from http_headers.visitors.rfc9110.weight import Weight


def test_acceptcharset_visitor():
    src = "*; q=1"
    expected = [(Token("*"), Weight(1.0))]
    visitor = AcceptCharsetVisitor()
    node = rfc9110.Rule("Accept-Charset").parse_all(src)
    assert visitor.visit(node) == expected
