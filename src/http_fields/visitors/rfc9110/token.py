from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_fields.parsedobjs import CaselessMixin, ParsedStr


class Token(CaselessMixin, ParsedStr):
    """Represents an RFC 9110 token."""

    parser = rfc9110.Rule("token")


class TokenVisitor(NodeVisitor):
    """Visits a token node."""

    @staticmethod
    def visit_token(node: Node) -> Token:
        return Token(node.value, parse=False)
