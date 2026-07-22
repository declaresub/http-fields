from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110.entitytag as entitytag


class ETagVisitor(NodeVisitor):
    """Helper class for parsing ETag header value."""

    visit_entity_tag = entitytag.EntityTagVisitor()

    def visit_etag(self, node: Node) -> entitytag.EntityTag:
        return next(filter(None, map(self.visit, node.children)))
