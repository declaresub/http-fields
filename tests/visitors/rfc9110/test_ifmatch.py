from typing import Literal

import pytest
from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.entitytag import EntityTag
from http_fields.visitors.rfc9110.ifmatch import IfMatchVisitor


@pytest.mark.parametrize(
    "src, expected",
    [
        ('"test"', [EntityTag("test")]),
        ("*", "*"),
        ("", []),
    ],
)
def test_ifmatch_visitor(src: str, expected: Literal["*"] | list[EntityTag]):
    node = rfc9110.Rule("if-match").parse_all(src)
    assert IfMatchVisitor().visit(node) == expected
