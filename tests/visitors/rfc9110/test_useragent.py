import pytest
from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.comment import Comment
from http_fields.visitors.rfc9110.product import Product
from http_fields.visitors.rfc9110.useragent import UserAgentVisitor


@pytest.mark.parametrize(
    "src, expected", [("Mozilla/5.0", [Product("Mozilla", "5.0")])]
)
def test_visit_user_agent(src: str, expected: list[Product | Comment]):
    node = rfc9110.Rule("User-Agent").parse_all(src)
    visitor = UserAgentVisitor()
    assert visitor.visit(node) == expected
