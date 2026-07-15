from datetime import datetime

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.httpdate as httpdate


class IfUnmodifiedSinceVisitor(NodeVisitor):
    visit_http_date = httpdate.HttpDateVisitor()

    def visit_if_unmodified_since(self, node: Node) -> datetime:
        return next(filter(None, map(self.visit, node.children)))
