"""Content-Disposition header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import ParseError, Rule
from abnf.grammars import rfc6266
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc6266 import (
    ContentDispositionNodeVisitor,
    DispExtParm,
    DispositionType,
    ExtValue,
    FilenameParm,
)


@dataclass(frozen=True)
class ContentDisposition(Header):
    """Content-Disposition header, as defined by RFC 6266."""

    name: ClassVar[str] = "Content-Disposition"
    rule: ClassVar[Rule] = rfc6266.Rule("content-disposition")
    visitor: ClassVar[ContentDispositionNodeVisitor] = ContentDispositionNodeVisitor()

    disposition_type: DispositionType
    disposition_parms: tuple[FilenameParm | DispExtParm, ...] = ()

    @classmethod
    def build(
        cls,
        disposition_type: str,
        disposition_parms: dict[str, str | ExtValue] | None = None,
    ) -> Self:
        """Build a Content-Disposition from a disposition type and a parameter mapping.

        A parameter named ``filename`` or ``filename*`` (case-insensitive) becomes a
        FilenameParm; anything else becomes a DispExtParm.
        """
        parms = tuple(
            FilenameParm(pname, pvalue)
            if pname.lower() in {"filename", "filename*"}
            else DispExtParm(pname, pvalue)
            for pname, pvalue in (disposition_parms or {}).items()
        )
        return cls(DispositionType(disposition_type), parms)

    @classmethod
    def parse(cls, value: str) -> Self:
        # unlike most header rules, 'content-disposition' matches the whole header line, so
        # we prepend the field name before parsing.
        cls._check_length(value)
        try:
            node = cls.rule.parse_all(f"content-disposition: {value}")
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc
        disposition_type, parms = cls.visitor.visit(node)
        return cls(disposition_type, tuple(parms))

    @property
    def value(self) -> str:
        return str(self.disposition_type) + "".join(
            f";{parm}" for parm in self.disposition_parms
        )
