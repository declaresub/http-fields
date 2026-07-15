import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.host import HostVisitor


@pytest.mark.parametrize(
    "src, expected",
    [
        ("www.example.com", ("www.example.com", None)),
        ("www.example.com:81", ("www.example.com", 81)),
    ],
)
def test_host_visitor(src: str, expected: tuple[str, int | None]):
    node = rfc9110.Rule("host").parse_all(src)
    visitor = HostVisitor()
    assert visitor.visit(node) == expected
