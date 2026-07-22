from typing import Literal

from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110.entitytag as entitytag


class IfMatchVisitor(NodeVisitor):
    visit_entity_tag = entitytag.EntityTagVisitor()

    @staticmethod
    def visit_literal(node: Node):
        return "*" if node.value == "*" else None

    def visit_if_match(self, node: Node) -> Literal["*"] | list[entitytag.EntityTag]:
        items = list(filter(None, map(self.visit, node.children)))
        if not items:
            empty_list: list[entitytag.EntityTag] = []
            return empty_list

        if items[0] == "*":
            return "*"
        else:
            return items
