from abnf import Node, NodeVisitor


class HostVisitor(NodeVisitor):
    def visit_host(self, node: Node) -> tuple[str, int | None]:
        # Match children by name: an empty uri-host ("") is valid (reg-name is
        # *(...)), and the ":" separator visits to None, so positional/truthiness
        # handling would mis-assign the port as the hostname.
        hostname = ""
        port: int | None = None
        for child in node.children:
            if child.name == "uri-host":
                hostname = self.visit(child)
            elif child.name == "port":
                port = self.visit(child)
        return (hostname, port)

    @staticmethod
    def visit_uri_host(node: Node):
        return node.value

    @staticmethod
    def visit_port(node: Node):
        # port = *DIGIT; an empty port ("example.com:") means no port.
        return int(node.value) if node.value else None
