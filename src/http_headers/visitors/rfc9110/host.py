from abnf import Node, NodeVisitor


class HostVisitor(NodeVisitor):
    def visit_host(self, node: Node) -> tuple[str, int | None]:
        items = filter(None, map(self.visit, node.children))
        hostname: str = next(items)
        port: int | None = next(items, None)
        return (hostname, port)

    @staticmethod
    def visit_uri_host(node: Node):
        return node.value

    @staticmethod
    def visit_port(node: Node):
        return int(node.value)
