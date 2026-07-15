"""Accept header class."""

from abnf import ParseError
from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AcceptEncodingVisitor, Weight, WeightedCoding


class AcceptEncoding(Header):
    """Accept-Encoding header, as defined by RFC 9110."""

    name = "accept-encoding"
    visitor = AcceptEncodingVisitor()

    def __init__(
        self,
        value: str | None = None,
        *,
        codings: list[tuple[str, float | Weight | None]] | None = None,
    ):
        if isinstance(value, str):
            self.value = value
        else:
            self.codings = [WeightedCoding(c, w) for c, w in codings] if codings else []

    @property
    def value(self):
        """Returns header value."""

        return ", ".join(str(coding) for coding in self.codings)

    @value.setter
    def value(self, val: str):
        rule = rfc9110.Rule("Accept-Encoding")
        try:
            node = rule.parse_all(val)
        except ParseError as exc:
            raise ValueError(f"Invalid {self.name} value.") from exc
        self.codings: list[WeightedCoding] = self.visitor.visit(node)
