from datetime import datetime

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.httpdate as httpdate


class RetryAfterVisitor(NodeVisitor):
    """NodeVisitor subclass for retry-after."""

    visit_http_date = httpdate.HttpDateVisitor()

    def visit_retry_after(self, node: Node) -> datetime | int:
        return self.visit(node.children[0])

    @staticmethod
    def visit_delay_seconds(node: Node) -> int:
        delay_seconds = int(node.value)
        assert delay_seconds >= 0  # if not, there is a parser issue.
        return delay_seconds
