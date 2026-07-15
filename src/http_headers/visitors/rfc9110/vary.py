from abnf import Node, NodeVisitor


class VaryVisitor(NodeVisitor):
    def visit_vary(self, node: Node) -> list[str]:
        return list(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_field_name(node: Node):
        return node.value
