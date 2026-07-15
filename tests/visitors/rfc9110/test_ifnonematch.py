from typing import Literal

import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.entitytag import EntityTag
from http_headers.visitors.rfc9110.ifnonematch import IfNoneMatchVisitor


@pytest.mark.parametrize(
    "src, expected",
    [
        ('"test"', [EntityTag("test")]),
        ("*", "*"),
        ("", []),
    ],
)
def test_ifnonematch_visitor(src: str, expected: Literal["*"] | list[EntityTag]):
    node = rfc9110.Rule("if-none-match").parse_all(src)
    assert IfNoneMatchVisitor().visit(node) == expected
