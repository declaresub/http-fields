from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.token as token


class AllowVisitor(NodeVisitor):
    visit_token = token.TokenVisitor()

    def visit_allow(self, node: Node) -> list[token.Token]:
        return list(filter(None, map(self.visit, node.children)))

    def visit_method(self, node: Node) -> token.Token:
        return next(filter(None, map(self.visit, node.children)))
