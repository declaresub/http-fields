from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.authparam as authparam
import http_headers.visitors.rfc9110.token68 as token68
from http_headers.visitors.rfc9110.authscheme import AuthScheme


@dataclass(frozen=True)
class AuthParamCredentials:
    scheme: AuthScheme
    auth_params: tuple[authparam.AuthParam, ...]

    def __init__(self, scheme: str, auth_params: list[authparam.AuthParam]):
        object.__setattr__(self, "scheme", AuthScheme(scheme))
        object.__setattr__(self, "auth_params", tuple(auth_params))

    def __str__(self):
        params = ",".join([str(param) for param in self.auth_params])
        return f"{self.scheme}{' ' + params if params else ''}"


@dataclass(frozen=True)
class TokenCredentials:
    scheme: AuthScheme
    token: token68.Token68 | None

    def __init__(self, scheme: str, token: str | None):
        object.__setattr__(self, "scheme", AuthScheme(scheme))
        object.__setattr__(self, "token", token68.Token68(token) if token else None)

    def __str__(self):
        return f"{self.scheme}{' ' + self.token if self.token else ''}"


class CredentialsVisitor(NodeVisitor):
    visit_token68 = token68.Token68Visitor()
    visit_auth_param = authparam.AuthParamVisitor()

    def visit_auth_scheme(self, node: Node):
        return AuthScheme(node.value)

    def visit_credentials(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        auth_scheme = next(items)
        assert isinstance(auth_scheme, AuthScheme)
        try:
            next_item = next(items)
        except StopIteration:
            return TokenCredentials(scheme=auth_scheme, token=None)
        else:
            if isinstance(next_item, token68.Token68):
                return TokenCredentials(scheme=auth_scheme, token=next_item)
            elif isinstance(next_item, authparam.AuthParam):
                auth_params = [next_item] + list(items)
                return AuthParamCredentials(scheme=auth_scheme, auth_params=auth_params)
            else:  # pragma: no cover
                raise AssertionError()


class AuthorizationVisitor(NodeVisitor):
    """NodeVisitor subclass for authorization header value."""

    visit_credentials = CredentialsVisitor()

    def visit_authorization(self, node: Node):
        return next(filter(None, map(self.visit, node.children)))


class ProxyAuthorizationVisitor(NodeVisitor):
    """NodeVisitor subclass for the Proxy-Authorization header value."""

    visit_credentials = CredentialsVisitor()

    def visit_proxy_authorization(self, node: Node):
        return next(filter(None, map(self.visit, node.children)))
