"""Base class for headers whose value is a single URI reference."""

from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import ParsedStr


@dataclass(frozen=True)
class UriHeader(Header):
    """Base for headers whose value is a single URI reference.

    Concrete subclasses supply ``name``, ``rule``, and ``uri_type`` -- a self-validating
    ParsedStr over that grammar rule. The uri validates on construction (not only via
    :meth:`parse`), so a raw constructor call cannot smuggle CR/LF/NUL or other invalid
    content into the serialized header.
    """

    uri_type: ClassVar[type[ParsedStr]]

    uri: ParsedStr

    def __init__(self, uri: str) -> None:
        # The uri self-validates as a leaf; an already-parsed value passes through.
        object.__setattr__(self, "uri", type(self).uri_type(uri))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    @property
    def value(self) -> str:
        return self.uri
