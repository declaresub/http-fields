"""Base class for headers whose value is a single URI reference."""

from dataclasses import dataclass

from typing_extensions import Self

from http_headers.header import Header


@dataclass(frozen=True)
class UriHeader(Header):
    """Base for headers whose value is a single URI reference.

    The URI is validated against the subclass's ``rule`` on construction (not only via
    :meth:`parse`) and stored as a string, so a raw constructor call cannot smuggle
    CR/LF/NUL or other invalid content into the serialized header. Concrete subclasses
    supply ``name`` and ``rule`` as ClassVars.
    """

    uri: str

    def __post_init__(self) -> None:
        self._validate_value()

    @classmethod
    def parse(cls, value: str) -> Self:
        # Construction validates against the grammar (__post_init__), and a full
        # parse_all match returns the whole input, so cls(value) is equivalent to
        # cls(_node(value).value) but parses once instead of twice.
        return cls(value)

    @property
    def value(self) -> str:
        return self.uri
