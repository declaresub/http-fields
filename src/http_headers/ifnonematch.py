"""If-None-Match header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.entitytaglist import EntityTagListHeader
from http_headers.visitors.rfc9110 import EntityTag, IfNoneMatchVisitor


class IfNoneMatch(EntityTagListHeader):
    """If-None-Match header, as defined by RFC 9110. ``wildcard`` (``*``) matches if any
    current representation exists."""

    name: ClassVar[str] = "If-None-Match"
    rule: ClassVar[Rule] = rfc9110.Rule("If-None-Match")
    visitor = IfNoneMatchVisitor()

    def matches(self, entity_tag: EntityTag) -> bool:
        """Return True if ``entity_tag`` weakly matches none of the tags; False if ``*``."""
        if self.wildcard:
            return False
        return not any(entity_tag.compare(tag, weak=True) for tag in self.entity_tags)
