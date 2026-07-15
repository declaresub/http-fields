from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_headers.parsedobjs import CaselessMixin, ParsedStr


class Token68(CaselessMixin, ParsedStr):
    """Represents an RFC 9110 token68."""

    parser = rfc9110.Rule("token68")


class Token68Visitor(NodeVisitor):
    """Visits a token68 node."""

    @staticmethod
    def visit_token68(node: Node) -> Token68:
        return Token68(node.value, parse=False)
