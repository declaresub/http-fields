from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.authparam as authparam
import http_headers.visitors.rfc9110.authscheme as authscheme
import http_headers.visitors.rfc9110.token68 as token68


@dataclass(frozen=True)
class TokenChallenge:
    scheme: authscheme.AuthScheme
    token: token68.Token68 | None

    def __init__(self, scheme: str, token: str | None):
        object.__setattr__(self, "scheme", authscheme.AuthScheme(scheme))
        object.__setattr__(self, "token", token68.Token68(token) if token else None)

    def __str__(self):
        return f"{self.scheme}{' ' + self.token if self.token else ''}"


@dataclass(frozen=True)
class AuthParamChallenge:
    scheme: authscheme.AuthScheme
    auth_params: tuple[authparam.AuthParam, ...]

    def __init__(self, scheme: str, auth_params: list[authparam.AuthParam]):
        object.__setattr__(self, "scheme", authscheme.AuthScheme(scheme))
        object.__setattr__(self, "auth_params", tuple(auth_params))

    def __str__(self):
        params = ",".join([str(param) for param in self.auth_params])
        return f"{self.scheme}{' ' + params if params else ''}"


class ChallengeVisitor(NodeVisitor):
    visit_token68 = token68.Token68Visitor()
    visit_auth_param = authparam.AuthParamVisitor()
    visit_auth_scheme = authscheme.AuthSchemeVisitor()

    def visit_challenge(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        auth_scheme = next(items)
        assert isinstance(auth_scheme, authscheme.AuthScheme)
        try:
            next_item = next(items)
        except StopIteration:
            return TokenChallenge(scheme=auth_scheme, token=None)
        else:
            if isinstance(next_item, token68.Token68):
                return TokenChallenge(scheme=auth_scheme, token=next_item)
            elif isinstance(next_item, authparam.AuthParam):
                auth_params = [next_item] + list(items)
                return AuthParamChallenge(scheme=auth_scheme, auth_params=auth_params)
            else:  # pragma: no cover
                raise AssertionError()
