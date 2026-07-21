"""Prefer and Preference-Applied header classes."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc7240
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc7240 import (
    Preference,
    PreferenceAppliedVisitor,
    PreferVisitor,
)


@dataclass(frozen=True)
class Prefer(Header):
    """Prefer header, as defined by RFC 7240."""

    name: ClassVar[str] = "Prefer"
    rule: ClassVar[Rule] = rfc7240.Rule("Prefer")
    rule_matches_line: ClassVar[bool] = True
    visitor: ClassVar[PreferVisitor] = PreferVisitor()

    preferences: tuple[Preference, ...]

    def __init__(self, *preferences: Preference) -> None:
        # Each Preference self-validates (Token name, leaf value, Param parameters), so
        # the field-type check fully guarantees a safe serialized value -- no re-parse.
        object.__setattr__(self, "preferences", tuple(preferences))

    @classmethod
    def parse(cls, value: str) -> Self:
        # the grammar rule matches the whole header line, so prepend the field name.
        return cls(*cls.visitor.visit(cls._prefixed_node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(pref) for pref in self.preferences)


@dataclass(frozen=True)
class PreferenceApplied(Header):
    """Preference-Applied header, as defined by RFC 7240."""

    name: ClassVar[str] = "Preference-Applied"
    rule: ClassVar[Rule] = rfc7240.Rule("Preference-Applied")
    rule_matches_line: ClassVar[bool] = True
    visitor: ClassVar[PreferenceAppliedVisitor] = PreferenceAppliedVisitor()

    preferences: tuple[Preference, ...]

    def __init__(self, *preferences: Preference) -> None:
        # Each Preference self-validates (Token name, leaf value, Param parameters), so
        # the field-type check fully guarantees a safe serialized value -- no re-parse.
        object.__setattr__(self, "preferences", tuple(preferences))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._prefixed_node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(pref) for pref in self.preferences)
