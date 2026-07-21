from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_headers.parsedobjs import CaselessMixin, ParsedStr


class AuthScheme(CaselessMixin, ParsedStr):
    """Represents an RFC 9110 auth-scheme. Schemes are case-insensitive
    (RFC 9110 section 11.1), so two schemes differing only in case compare equal;
    the original casing is preserved on serialization."""

    parser = rfc9110.Rule("auth-scheme")


class AuthSchemeVisitor(NodeVisitor):
    def visit_auth_scheme(self, node: Node):
        return AuthScheme(node.value)
