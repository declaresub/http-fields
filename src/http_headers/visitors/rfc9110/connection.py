from abnf import Node, NodeVisitor

from http_headers.visitors.rfc9110.token import Token, TokenVisitor


class ConnectionVisitor(NodeVisitor):
    visit_token = TokenVisitor()

    def visit_connection_option(self, node: Node) -> list[Token]:
        return next(filter(None, map(self.visit, node.children)))

    def visit_connection(self, node: Node) -> list[Token]:
        return list(filter(None, map(self.visit, node.children)))
