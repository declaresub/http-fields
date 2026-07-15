"""Vary header class."""

from abnf.grammars import rfc7231
from abnf.parser import ParseError

from http_headers.header import Header
from http_headers.visitors.rfc9110 import VaryVisitor


class Vary(Header):
    """Vary header.

    Vary: accept-encoding, accept-language
    """

    name = "Vary"

    def __init__(
        self, value: str | None = None, *, field_names: list[str] | None = None
    ):
        if value is None:
            for field_name in field_names if field_names else []:
                try:
                    rfc7231.Rule("Vary").parse_all(field_name)
                except ParseError as exc:
                    raise ValueError(f"Invalid field name {field_name}.") from exc
            self.field_names = list(field_names) if field_names else []
        else:
            self.value = value

    @property
    def value(self):
        return ", ".join(self.field_names) if self.field_names else "*"

    @value.setter
    def value(self, val: str):
        try:
            node = rfc7231.Rule("Vary").parse_all(val)
        except ParseError as exc:
            raise ValueError(f"Invalid Vary value {val}.") from exc
        visitor = VaryVisitor()
        self.field_names = visitor.visit(node)
