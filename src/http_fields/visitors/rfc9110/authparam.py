from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110.quotedstring as quotedstring
import http_fields.visitors.rfc9110.token as token


@dataclass(frozen=True)
class AuthParam:
    name: token.Token
    value: token.Token | quotedstring.QuotedString

    def __init__(self, name: str, value: str):
        object.__setattr__(self, "name", token.Token(name))

        if name.lower() == "realm":
            # realm value should be quoted.  See https://tools.ietf.org/html/rfc7235#section-2.2.
            object.__setattr__(self, "value", quotedstring.QuotedString(value))
        else:
            try:
                object.__setattr__(self, "value", token.Token(value))
            except ValueError:
                object.__setattr__(self, "value", quotedstring.QuotedString(value))

    def __str__(self):
        return f"{self.name}={self.value}"


class AuthParamVisitor(NodeVisitor):
    visit_token = token.TokenVisitor()
    visit_quoted_string = quotedstring.QuotedStringVisitor()

    def visit_auth_param(self, node: Node):
        name: token.Token
        value: token.Token | quotedstring.QuotedString
        name, value = filter(None, map(self.visit, node.children))
        assert isinstance(name, token.Token)
        assert isinstance(value, token.Token | quotedstring.QuotedString)
        return AuthParam(name=name, value=value)
