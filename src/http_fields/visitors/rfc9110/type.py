from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110.token as token


class TypeVisitor(NodeVisitor):
    visit_token = token.TokenVisitor()

    def visit_type(self, node: Node):
        return next(filter(None, map(self.visit, node.children)))


class SubtypeVisitor(NodeVisitor):
    visit_token = token.TokenVisitor()

    def visit_subtype(self, node: Node):
        return next(filter(None, map(self.visit, node.children)))
