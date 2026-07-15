import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.entitytag import EntityTag, EntityTagVisitor


def test_entitytag():
    assert EntityTag("deadbeef", weak=False)


def test_entitytag_bad_tag():
    with pytest.raises(ValueError):
        EntityTag('"')


def test_entitytag_hash():
    assert hash(EntityTag("deadbeef", weak=False))


@pytest.mark.parametrize(
    "tag1, tag2, weak, expected",
    [
        (EntityTag("1", weak=True), EntityTag("1", weak=True), False, False),
        (EntityTag("1", weak=True), EntityTag("2", weak=True), False, False),
        (EntityTag("1", weak=True), EntityTag("1", weak=False), False, False),
        (EntityTag("1", weak=False), EntityTag("1", weak=False), False, True),
        (EntityTag("1", weak=True), EntityTag("1", weak=True), True, True),
        (EntityTag("1", weak=True), EntityTag("2", weak=True), True, False),
        (EntityTag("1", weak=True), EntityTag("1", weak=False), True, True),
        (EntityTag("1", weak=False), EntityTag("1", weak=False), True, True),
    ],
)
def test_entitytag_compare(
    tag1: EntityTag, tag2: EntityTag, weak: bool, expected: bool
):
    assert tag1.compare(tag2, weak=weak) == expected


def test_entitytag_compare_to_something_else():
    with pytest.raises(TypeError):
        assert EntityTag("1", weak=True).compare("test", weak=True)


@pytest.mark.parametrize(
    "src, expected",
    [
        ('W/"test"', EntityTag("test", weak=True)),
        # ('"test"', EntityTag("test", weak=False)),
    ],
)
def test_entity_tag_visitor(src: str, expected: EntityTag):
    node = rfc9110.Rule("entity-tag").parse_all(src)
    entity_tag = EntityTagVisitor().visit(node)
    print(entity_tag)
    print(expected)
    assert entity_tag == expected
