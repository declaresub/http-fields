from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.connection import ConnectionVisitor
from http_fields.visitors.rfc9110.token import Token


def test_comnectionvisitor():
    src = "foo, bar"
    node = rfc9110.Rule("Connection").parse_all(src)
    directives = ConnectionVisitor().visit(node)
    assert directives == [Token("foo"), Token("bar")]
