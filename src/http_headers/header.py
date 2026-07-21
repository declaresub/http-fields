"""HTTP header abstract base class and the generic custom-header class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

from abnf import Node, ParseError, Rule
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110 import FieldName, FieldValue


class Header(ABC):
    """Abstract base for HTTP headers.

    Known headers are frozen dataclasses whose fields are the structured components of the
    header value. Each sets ``name`` (and usually ``rule``/``visitor``) as a ClassVar,
    implements a ``parse(value)`` classmethod, and exposes a derived ``value`` property.
    Arbitrary headers (e.g. ``X-Request-Id``) are represented by :class:`CustomHeader`.
    """

    encoding: ClassVar[str] = "ISO-8859-1"
    rule: ClassVar[Rule]  # abnf rule for the header value; provided by subclasses
    name: ClassVar[str]  # field name; a class constant on known headers,
    # overridden by a per-instance property on CustomHeader.

    @property
    @abstractmethod
    def value(self) -> str:
        """The serialized header field value (without the name)."""

    def __str__(self) -> str:
        """Return the full ``Name: value`` header field."""
        return f"{self.name}: {self.value}"

    def __bytes__(self) -> bytes:
        return str(self).encode(self.encoding)

    @property
    def asgi_value(self) -> tuple[bytes, bytes]:
        """Return a ``(name, value)`` pair of latin-1 bytes for an ASGI send dict.

        ASGI encodes header values as ISO-8859-1 (latin-1); using the class
        encoding keeps this consistent with ``__bytes__`` and accepts obs-text.
        """
        return (self.name.encode(self.encoding), self.value.encode(self.encoding))

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, Header) and type(other) is type(self):
            return (self.name, self.value) == (other.name, other.value)
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.name, self.value))

    @classmethod
    def _node(cls, value: str) -> Node:
        """Parse ``value`` against ``cls.rule``, translating a ParseError to a ValueError."""
        try:
            return cls.rule.parse_all(value)
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc

    @classmethod
    def _prefixed_node(cls, value: str) -> Node:
        """Like :meth:`_node`, but for grammar rules that match the whole header line (name
        included); prepend ``"<name>: "`` before parsing."""
        try:
            return cls.rule.parse_all(f"{cls.name}: {value}")
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc

    @classmethod
    def parse(cls, value: str) -> Header:
        """Parse a header value into an instance. Every concrete known header overrides this
        (CustomHeader carries an arbitrary name and is built via its constructor instead)."""
        raise NotImplementedError

    @classmethod
    def create(cls, name: str, value: str) -> Header:
        """Return a header for ``(name, value)``: a matching known subclass if one is
        registered for ``name``, otherwise a :class:`CustomHeader`."""
        lname = name.lower()
        for subcls in cls.subclass_tree():
            cls_name = getattr(subcls, "name", None)
            if isinstance(cls_name, str) and cls_name.lower() == lname:
                return subcls.parse(value)
        return CustomHeader(name, value)

    @classmethod
    def subclass_tree(cls) -> Iterable[type[Header]]:
        """Yield all Header subclasses, depth-first."""
        for subcls in cls.__subclasses__():
            yield subcls
            yield from subcls.subclass_tree()


@dataclass(frozen=True)
class CustomHeader(Header):
    """A header with an arbitrary field name, e.g. ``X-Request-Id``.

    Both name and value are validated against RFC 9110 (``field-name`` / ``field-value``).
    """

    rule: ClassVar[Rule] = rfc9110.Rule("field-value")

    field_name: FieldName
    field_value: FieldValue

    def __init__(self, name: str, value: str) -> None:
        object.__setattr__(self, "field_name", FieldName(name))
        object.__setattr__(self, "field_value", FieldValue(value))

    @property
    def name(self) -> str:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self.field_name

    @property
    def value(self) -> str:
        return self.field_value
