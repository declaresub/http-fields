"""Priority header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import ParseError, Rule
from abnf.grammars import rfc9651
from typing_extensions import Self

from http_headers.header import Header
from http_headers.structuredfields import Item, parse_dictionary, serialize_dictionary


@dataclass(frozen=True)
class Priority(Header):
    """Priority header, as defined by RFC 9218: a Structured Fields Dictionary with an
    ``urgency`` (0-7, default 3) and an ``incremental`` flag (default False). Default values
    are omitted from the serialized value."""

    name: ClassVar[str] = "priority"
    rule: ClassVar[Rule] = rfc9651.Rule("sf-dictionary")

    urgency: int = 3
    incremental: bool = False

    @classmethod
    def parse(cls, value: str) -> Self:
        try:
            members = dict(parse_dictionary(value))
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc
        urgency = 3
        incremental = False
        u = members.get("u")
        if (
            isinstance(u, Item)
            and isinstance(u.value, int)
            and not isinstance(u.value, bool)
            and 0 <= u.value <= 7
        ):
            urgency = u.value
        i = members.get("i")
        if isinstance(i, Item) and isinstance(i.value, bool):
            incremental = i.value
        return cls(urgency, incremental)

    @property
    def value(self) -> str:
        members: list[tuple[str, Item]] = []
        if self.urgency != 3:
            members.append(("u", Item(self.urgency)))
        if self.incremental:
            members.append(("i", Item(True)))
        return serialize_dictionary(tuple(members))
