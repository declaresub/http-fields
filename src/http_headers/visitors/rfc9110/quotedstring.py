from abnf import LiteralNode, Node, NodeVisitor
from abnf.grammars import rfc9110

from http_headers.parsedobjs import ParsedStr


class QuotedPairVisitor(NodeVisitor):
    def visit_quoted_pair(self, node: Node) -> str:
        assert (
            isinstance(node.children[0], LiteralNode) and node.children[0].value == "\\"
        )
        return self.visit(node.children[1])

    @staticmethod
    def visit_htab(node: Node) -> str:
        return node.value

    @staticmethod
    def visit_sp(node: Node) -> str:
        return node.value

    @staticmethod
    def visit_vchar(node: Node) -> str:
        return node.value

    @staticmethod
    def visit_obs_text(node: Node) -> str:
        return node.value


class QuotedString(ParsedStr):
    """Represents an RFC 9110 quoted-string.
    A QuotedString can be created either double-quoted or not; the result will be a double-quoted
    string, escaped as needed."""

    parser = rfc9110.Rule("quoted-string")

    def __new__(cls, s: str, parse: bool = True):
        assert isinstance(s, str)
        if isinstance(s, cls):
            return s
        else:
            # if s is double-quoted, we parse as is.  if not, we escape what needs to be escaped,
            # wrap in double quotes, and parse that.
            if s == "":
                dquoted_value = '""'
            elif len(s) > 1 and s[0] == '"' and s[-1] == '"':
                dquoted_value = s
            else:
                escaped_value = "".join(f"\\{x}" if x in ["\\", '"'] else x for x in s)
                dquoted_value = f'"{escaped_value}"'
            return super().__new__(cls, dquoted_value)


class QuotedStringVisitor(NodeVisitor):
    """Visits an RFC 9110 quoted-string."""

    visit_quoted_pair = QuotedPairVisitor()

    def visit_quoted_string(self, node: Node) -> QuotedString:
        value = "".join(x for x in map(self.visit, node.children) if x is not None)
        return QuotedString(value, parse=False)

    @staticmethod
    def visit_qdtext(node: Node) -> str:
        return node.value
