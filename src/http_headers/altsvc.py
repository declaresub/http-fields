"""Alt-Svc and Alt-Used header classes."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc7838
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc7838 import AltSvcVisitor, AltValue


@dataclass(frozen=True)
class AltSvc(Header):
    """Alt-Svc header, as defined by RFC 7838. The special value ``clear`` is represented by
    ``clear=True`` with no ``values``."""

    name: ClassVar[str] = "Alt-Svc"
    rule: ClassVar[Rule] = rfc7838.Rule("Alt-Svc")
    visitor: ClassVar[AltSvcVisitor] = AltSvcVisitor()

    values: tuple[AltValue, ...] = ()
    clear: bool = False

    def __init__(self, *values: AltValue, clear: bool = False) -> None:
        object.__setattr__(self, "values", tuple(values))
        object.__setattr__(self, "clear", clear)

    @classmethod
    def parse(cls, value: str) -> Self:
        if value.strip().lower() == "clear":
            cls._node(value)  # validate
            return cls(clear=True)
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return "clear" if self.clear else ", ".join(str(v) for v in self.values)


@dataclass(frozen=True)
class AltUsed(Header):
    """Alt-Used header, as defined by RFC 7838: the alternative authority actually used."""

    name: ClassVar[str] = "Alt-Used"
    rule: ClassVar[Rule] = rfc7838.Rule("Alt-Used")

    authority: str

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls._node(value).value)

    @property
    def value(self) -> str:
        return self.authority
