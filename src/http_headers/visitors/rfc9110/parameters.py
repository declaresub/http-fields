from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.quotedstring as quotedstring
import http_headers.visitors.rfc9110.token as token

__all__ = ["Parameter", "ParameterVisitor", "ParametersVisitor"]


Token = token.Token
TokenVisitor = token.TokenVisitor
QuotedString = quotedstring.QuotedString
QuotedStringVisitor = quotedstring.QuotedStringVisitor


@dataclass
class Parameter:
    name: Token
    value: Token | QuotedString

    def __init__(self, name: str, value: str):
        self.name = Token(name)
        try:
            self.value = Token(value)
        except ValueError:
            self.value = QuotedString(value)

    def __str__(self):
        return f"{self.name}={self.value}"


class ParameterVisitor(NodeVisitor):
    visit_quoted_string = QuotedStringVisitor()
    visit_token = TokenVisitor()

    def visit_parameter(self, node: Node):
        name: Token
        value: Token | QuotedString
        name, value = filter(None, map(self.visit, node.children))
        return Parameter(name, value)

    def visit_parameter_name(self, node: Node) -> Token:
        return next(filter(None, map(self.visit, node.children)))

    def visit_parameter_value(self, node: Node) -> Token | QuotedString:
        return next(filter(None, map(self.visit, node.children)))


class ParametersVisitor(NodeVisitor):
    visit_parameter = ParameterVisitor()

    def visit_parameters(self, node: Node) -> list[Parameter]:
        return list(filter(None, map(self.visit, node.children)))
