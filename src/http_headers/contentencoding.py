"""ContentEncoding header class"""

from abnf.grammars import rfc9110
from abnf.parser import Node, NodeVisitor

from http_headers.header import Header


class ContentEncodingVisitor(NodeVisitor):
    def visit_content_encoding(self, node: Node) -> list[str]:
        return list(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_content_coding(node: Node) -> str:
        return node.value


class ContentEncoding(Header):
    """Content-Encoding header.
    Usage:
        header = ContentEncoding('deflate, gzip')
        header = ContentEncoding(['deflate', 'gzip'])

        In the second case, list items are parsed to ensure that they are valid.
    """

    name = "content-encoding"
    visitor = ContentEncodingVisitor()

    def __init__(self, value: str | list[str]):

        if isinstance(value, str):
            self.value = value

        elif isinstance(value, list):  # type: ignore
            self.value = ",".join(value)
        else:
            raise TypeError("value must be str or list[str].")

    @property
    def value(self):
        return ", ".join(self.content_coding)

    @value.setter
    def value(self, val: str):
        rule = rfc9110.Rule("Content-Encoding")
        node = rule.parse_all(val)
        self.content_coding: list[str] = self.visitor.visit(node)
