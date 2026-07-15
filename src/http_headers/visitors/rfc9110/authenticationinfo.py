from abnf import Node, NodeVisitor

from http_headers.visitors.rfc9110.authparam import AuthParam, AuthParamVisitor


class AuthenticationInfoVisitor(NodeVisitor):
    visit_auth_param = AuthParamVisitor()

    def visit_authentication_info(self, node: Node) -> list[AuthParam]:
        items = filter(None, map(self.visit, node.children))
        return list(items)
