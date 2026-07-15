from abnf.grammars import rfc9110

from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9110.contentlength import ContentLengthVisitor


def test_contentlength_visitor():
    src = "43"
    node = rfc9110.Rule("Content-Length").parse_all(src)
    visitor = ContentLengthVisitor()
    assert visitor.visit(node) == NonNegativeInt(43)
