"""If-Match header class, and visitor."""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import EntityTag, FieldName, IfMatchVisitor


class IfMatch(Header):
    name = FieldName("If-Match")
    visitor = IfMatchVisitor()

    def __init__(self, value: str | EntityTag | list[EntityTag]):
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, EntityTag):
            self.entity_tags = [value]
            self.match_any = False
        elif isinstance(value, list):  # type: ignore
            self.entity_tags = list(value)
            self.match_any = False
        else:  # pragma: no cover
            raise TypeError("value must be str, EntityTag, or list[EntityTag]")

    @property
    def value(self):
        return (
            "*" if self.match_any else ", ".join(str(etag) for etag in self.entity_tags)
        )

    @value.setter
    def value(self, val: str):
        node = rfc9110.Rule("If-Match").parse_all(val)
        result = self.visitor.visit(node)
        if result == "*":
            self.match_any = True
            self.entity_tags = []
        else:
            self.match_any = False
            self.entity_tags = result

    def matches(self, entity_tag: EntityTag):
        # matches returns True if self.value == "*".  In this case, if-match should succeed if the origin server
        # has a current representation for the target resource.

        if self.match_any:
            return True
        else:
            return any(entity_tag.compare(tag, weak=False) for tag in self.entity_tags)
