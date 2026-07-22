from abnf import Node, NodeVisitor

from http_fields.parsedobjs import NonNegativeInt


class ContentLengthVisitor(NodeVisitor):
    @staticmethod
    def visit_content_length(node: Node):
        return NonNegativeInt(node.value)
