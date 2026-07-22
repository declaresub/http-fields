from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110.comment as comment
import http_fields.visitors.rfc9110.product as product
import http_fields.visitors.rfc9110.token as token

__all__ = ["UserAgentVisitor"]


class UserAgentVisitor(NodeVisitor):
    visit_comment = comment.CommentVisitor()
    visit_product = product.ProductVisitor()
    visit_token = token.TokenVisitor()

    def visit_user_agent(self, node: Node) -> list[product.Product | comment.Comment]:
        return list(filter(None, map(self.visit, node.children)))
