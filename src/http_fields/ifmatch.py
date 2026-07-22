"""If-Match header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_fields.entitytaglist import EntityTagListHeader
from http_fields.visitors.rfc9110 import EntityTag, IfMatchVisitor


class IfMatch(EntityTagListHeader):
    """If-Match header, as defined by RFC 9110. ``wildcard`` (``*``) matches any current
    representation."""

    name: ClassVar[str] = "If-Match"
    rule: ClassVar[Rule] = rfc9110.Rule("If-Match")
    visitor = IfMatchVisitor()

    def matches(self, entity_tag: EntityTag) -> bool:
        """Return True if ``entity_tag`` strongly matches, or this header is ``*``."""
        if self.wildcard:
            return True
        return any(entity_tag.compare(tag, weak=False) for tag in self.entity_tags)
