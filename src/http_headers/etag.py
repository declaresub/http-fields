"""ETag header class, and visitors."""

from __future__ import annotations

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import EntityTag, ETagVisitor, FieldName


class ETag(Header):
    """Represents an ETag header."""

    name = FieldName("ETag")
    visitor = ETagVisitor()

    def __init__(self, value: str | None = None, *, tag: str = "", weak: bool = False):
        """
        Pass either a tag and optional weak flag, or a value.

        :param tag: a str containing the tag value, not double-quoted.
        :param weak: a bool representing whether or not the ETag is weak.
        :param value: a str containing a header value.
        """

        if isinstance(value, str):
            self.value = value
        else:
            self.entity_tag = EntityTag(tag, weak=weak)

    @property
    def value(self):
        """Returns the ETag header value."""
        return str(self.entity_tag)

    @value.setter
    def value(self, val: str):
        node = rfc9110.Rule("ETag").parse_all(val)
        self.entity_tag: EntityTag = self.visitor.visit(node)

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, self.__class__) and self.entity_tag == __o.entity_tag

    def __hash__(self):
        return hash(self.entity_tag)

    def matches(self, entity_tag: EntityTag | None, weak: bool = False):
        """Compare etag to an entity tag generated for resource.  Returns True if match succeeds, False if not. Comparison
        to Nane is supported."""

        return (
            self.entity_tag.compare(entity_tag, weak=weak)
            if isinstance(entity_tag, EntityTag)
            else False
        )
