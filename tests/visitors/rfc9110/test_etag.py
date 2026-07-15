import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.entitytag import EntityTag
from http_headers.visitors.rfc9110.etag import ETagVisitor


@pytest.mark.parametrize(
    "src, expected",
    [
        ('W/"test"', EntityTag("test", weak=True)),
    ],
)
def test_etag_visitor(src: str, expected: EntityTag):
    node = rfc9110.Rule("etag").parse_all(src)
    entity_tag = ETagVisitor().visit(node)
    assert entity_tag == expected
