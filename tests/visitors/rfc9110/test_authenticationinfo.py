import pytest
from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110 import AuthenticationInfoVisitor, AuthParam


@pytest.mark.parametrize(
    "src, expected",
    [
        ("", []),
        ("name=value, foo=bar", [AuthParam("name", "value"), AuthParam("foo", "bar")]),
    ],
)
def test_authenticationinfovisitor(src: str, expected: list[AuthParam]):
    src = "name=value, foo=bar"
    node = rfc9110.Rule("Authentication-Info").parse_all(src)
    visitor = AuthenticationInfoVisitor()
    assert visitor.visit(node) == [AuthParam("name", "value"), AuthParam("foo", "bar")]
