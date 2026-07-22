"""Base classes for headers whose value is a Structured Field (RFC 9651)."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import ParseError, Rule
from abnf.grammars import rfc9651
from typing_extensions import Self

from http_headers.header import Header
from http_headers.structuredfields import (
    InnerList,
    Item,
    parse_dictionary,
    parse_list,
    serialize_dictionary,
    serialize_list,
)


@dataclass(frozen=True)
class StructuredListHeader(Header):
    """Base for headers that are a Structured Fields List (Cache-Status, Proxy-Status)."""

    rule: ClassVar[Rule] = rfc9651.Rule("sf-list")

    members: tuple[Item | InnerList, ...]

    def __init__(self, *members: Item | InnerList) -> None:
        object.__setattr__(self, "members", tuple(members))
        # Check field types first, so a wrong-typed member gets the contract's TypeError
        # (pointing at parse()) rather than tripping the serializer's Item assertions below.
        self._check_field_types()
        # Serializing validates every member (rejecting injection / out-of-range values
        # via serialize_bare) and caches the result; a valid serialization is grammar-valid
        # by construction, so no re-parse is needed.
        _ = self.value

    @classmethod
    def parse(cls, value: str) -> Self:
        cls._check_length(value)
        try:
            return cls(*parse_list(value))
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc

    @property
    def value(self) -> str:
        return serialize_list(self.members)


@dataclass(frozen=True)
class DigestHeader(Header):
    """Base for headers that are a Structured Fields Dictionary of byte-sequence digests
    (Content-Digest, Repr-Digest)."""

    rule: ClassVar[Rule] = rfc9651.Rule("sf-dictionary")

    digests: tuple[tuple[str, bytes], ...]

    def __init__(self, *digests: tuple[str, bytes]) -> None:
        object.__setattr__(self, "digests", tuple(digests))
        # Check field types first, so a wrong-typed member gets the contract's TypeError
        # (pointing at parse()) rather than an unpack/serializer error below.
        self._check_field_types()
        # Serializing validates every dictionary key (via _validate_key) and caches the
        # result; a valid serialization is grammar-valid by construction, so no re-parse.
        _ = self.value

    @classmethod
    def parse(cls, value: str) -> Self:
        cls._check_length(value)
        try:
            members = parse_dictionary(value)
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc
        digests: list[tuple[str, bytes]] = []
        for key, m in members:
            # Each digest value must be a byte sequence; anything else is
            # malformed and must be rejected rather than silently discarded.
            if not (isinstance(m, Item) and isinstance(m.value, bytes)):
                raise ValueError(
                    f"{cls.__name__} member {key!r} is not a byte sequence."
                )
            digests.append((key, m.value))
        return cls(*digests)

    @property
    def value(self) -> str:
        return serialize_dictionary(tuple((key, Item(d)) for key, d in self.digests))
