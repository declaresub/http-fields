from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_headers.parsedobjs import ParsedStr


class AuthScheme(ParsedStr):
    """Represents an RFC 9110 auth-scheme."""

    parser = rfc9110.Rule("auth-scheme")


class AuthSchemeVisitor(NodeVisitor):
    def visit_auth_scheme(self, node: Node):
        return AuthScheme(node.value)
