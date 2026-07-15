"""WWWAuthenticate header class."""

from abnf.grammars import rfc9110
from abnf.parser import ParseError

from http_headers.header import Header
from http_headers.visitors.rfc9110 import (
    AuthParam,
    AuthParamChallenge,
    FieldName,
    TokenChallenge,
    WWWAuthenticateVisitor,
)

__all__ = ["AuthParam", "AuthParamChallenge", "TokenChallenge", "WWWAuthenticate"]


class WWWAuthenticate(Header):
    """WWW-Authenticate header."""

    name = FieldName("www-authenticate")

    def __init__(
        self,
        value: str | None = None,
        *,
        challenges: list[TokenChallenge | AuthParamChallenge] | None = None,
    ):
        """Intializes a WWW-Authenticate header."""

        if value is None:
            self.challenges = list(challenges) if challenges else []
        else:
            self.value = value

    @property
    def value(self):
        return ", ".join(str(challenge) for challenge in self.challenges)

    @value.setter
    def value(self, val: str):
        try:
            node = rfc9110.Rule("WWW-Authenticate").parse_all(val)
        except ParseError as exc:
            raise ValueError(f'Invalid {self.name} header value "{val}".') from exc
        else:
            visitor = WWWAuthenticateVisitor()
            self.challenges: list[TokenChallenge | AuthParamChallenge] = visitor.visit(
                node
            )
