from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_fields.parsedobjs import CaselessMixin, NonNegativeInt, ParsedStr


class Hostname(CaselessMixin, ParsedStr):
    """An RFC 9110 uri-host. Compares case-insensitively while preserving the original
    text; self-validating."""

    parser = rfc9110.Rule("uri-host")


class HostVisitor(NodeVisitor):
    def visit_host(self, node: Node) -> tuple[Hostname, NonNegativeInt | None]:
        # Match children by name: an empty uri-host ("") is valid (reg-name is
        # *(...)), and the ":" separator visits to None, so positional/truthiness
        # handling would mis-assign the port as the hostname. The node is already
        # parsed, so wrap its text as leaves untrusted-free (parse=False).
        hostname = Hostname("", parse=False)
        port: NonNegativeInt | None = None
        for child in node.children:
            if child.name == "uri-host":
                hostname = Hostname(child.value, parse=False)
            elif child.name == "port":
                port = self.visit(child)
        return (hostname, port)

    @staticmethod
    def visit_port(node: Node) -> NonNegativeInt | None:
        # port = *DIGIT; an empty port ("example.com:") means no port.
        return NonNegativeInt(node.value) if node.value else None
