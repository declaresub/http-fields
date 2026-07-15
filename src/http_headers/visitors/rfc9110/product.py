from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.comment as comment
import http_headers.visitors.rfc9110.token as token

Token = token.Token
TokenVisitor = token.TokenVisitor


__all__ = ["Product", "ProductVisitor"]


@dataclass
class Product:
    name: Token
    version: Token | None

    def __init__(self, name: str, version: str | None = None):
        self.name = Token(name)
        self.version = Token(version) if version else None

    def __str__(self):
        return str(self.name) + f"/{self.version}" if self.version else ""


class ProductVisitor(NodeVisitor):
    visit_comment = comment.CommentVisitor()
    visit_token = TokenVisitor()

    def visit_product(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        name = next(items)
        version = next(items, None)
        return Product(name, version)

    def visit_product_version(self, node: Node) -> Token:
        return next(filter(None, map(self.visit, node.children)))
