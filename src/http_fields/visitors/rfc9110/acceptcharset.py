from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110._base as base
import http_fields.visitors.rfc9110.token as token
import http_fields.visitors.rfc9110.weight as weight

Token = token.Token
TokenVisitor = token.TokenVisitor
Weight = weight.Weight
WeightVisitor = weight.WeightVisitor


class AcceptCharsetVisitor(NodeVisitor):
    visit_token = TokenVisitor()
    visit_weight = WeightVisitor()

    def visit_accept_charset(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        charsets = list(base.transform(items, Token, Weight))
        return charsets

    # the accept-charset value "*" is matched by the RFC 9110 rule 'token', so
    # the parser will usually recognize it as a token in the alternation 'token / "*".
    # we have this method just in case, but skip testing it.
    def visit_literal(self, node: Node):  # pragma: no cover
        return Token("*") if node.value == "*" else None
