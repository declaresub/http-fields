"""ContentDisposition header class"""

from typing import Any

from abnf.grammars import rfc6266

from http_headers.header import Header
from http_headers.visitors.rfc6266 import (
    ContentDispositionNodeVisitor,
    DispExtParm,
    DispositionType,
    ExtValue,
    Filename,
    FilenameParm,
)


class ContentDisposition(Header):
    """Content-Disposition header."""

    name = "Content-Disposition"
    visitor = ContentDispositionNodeVisitor()

    def __init__(
        self,
        value: str | None = None,
        *,
        disposition_type: str | None = None,
        disposition_parms: dict[str, str | ExtValue] | None = None,
    ):
        if isinstance(value, str):
            self.value = value
        elif isinstance(disposition_type, str):
            self.disposition_type = DispositionType(disposition_type)
            parm_list = [
                FilenameParm(parm_name, parm_value)
                if parm_name in {Filename("filename"), Filename("filename*")}
                else DispExtParm(parm_name, parm_value)
                for parm_name, parm_value in (
                    disposition_parms if disposition_parms else {}
                ).items()
            ]
            self.disposition_parms = {p.name: p.value for p in parm_list}
        else:
            raise TypeError("Either value or disposition_type must be str.")

    @property
    def value(self):
        """Returns header value."""
        parm_list = [
            FilenameParm(name, value)
            if isinstance(name, Filename)
            else DispExtParm(name, value)
            for name, value in self.disposition_parms.items()
        ]
        return str(self.disposition_type) + "".join(f";{parm}" for parm in parm_list)

    @value.setter
    def value(self, val: str):
        rule = rfc6266.Rule("content-disposition")
        # unlike most http header grammar rules, the rule 'content-disposition' defines the entire header, not
        # just the value. So we must prepend the header name.
        node = rule.parse_all(f"content-disposition: {val}")
        disposition_type: DispositionType
        disposition_parms: list[FilenameParm | DispExtParm]
        disposition_type, disposition_parms = self.visitor.visit(node)
        self.disposition_type = disposition_type
        self.disposition_parms = {p.name: p.value for p in disposition_parms}

    def __eq__(self, other: Any):
        return (
            self.disposition_type == other.disposition_type
            and self.disposition_parms == other.disposition_parms
            if isinstance(other, self.__class__)
            else NotImplemented
        )
