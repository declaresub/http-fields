"""Base class for headers whose value is a single URI reference."""

from dataclasses import dataclass

from typing_extensions import Self

from http_headers.header import Header


@dataclass(frozen=True)
class UriHeader(Header):
    """Base for headers whose value is a single URI reference.

    The URI is validated against the subclass's ``rule`` and stored as a string. Concrete
    subclasses supply ``name`` and ``rule`` as ClassVars.
    """

    uri: str

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls._node(value).value)

    @property
    def value(self) -> str:
        return self.uri
