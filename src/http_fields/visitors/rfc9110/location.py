from abnf import Node, NodeVisitor

__all__ = ["LocationVisitor"]


class LocationVisitor(NodeVisitor):
    def visit_location(self, node: Node):
        # in the future, this might be replaced with a more detailed uri object.
        return node.value
