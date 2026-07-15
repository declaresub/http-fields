"""HTTP header base class."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, cast

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110 import FieldName, FieldValue


class HeaderSubclass(Protocol):
    def __init__(self, value: str): ...  # pragma: no cover


class Header:
    """Class for custom headers (e.g. X-Request-Id). Header name and value are checked
    for RFC 7230 compliance.

    Explain assumptions about subclass interface -- name attribute, __init__ should have a value parameter

    """

    encoding: str = "ISO-8859-1"
    # override this in subclasses as appropriate
    value_rule: Rule = rfc9110.Rule("field-value")

    def __init__(self, name: str, value: str):
        assert isinstance(name, str), "name must be a str."
        assert isinstance(value, str), "value must be a str."
        self.name = FieldName(name)
        self.value = FieldValue(value)

    def __eq__(self, __o: object) -> bool:
        return (
            (self.name, self.value) == (__o.name, __o.value)
            if isinstance(__o, self.__class__) and isinstance(self, __o.__class__)
            else NotImplemented
        )

    def __hash__(self) -> int:
        return hash((self.name, self.value))

    def __str__(self) -> str:
        """Returns the header field."""
        return f"{self.name}: {self.value}"

    def __bytes__(self) -> bytes:
        return str(self).encode(self.encoding)

    @property
    def asgi_value(self) -> tuple[bytes, bytes]:
        """Returns a 2-tuple (name, value) suitable for use in asgi send dict."""
        return (self.name.encode("ascii"), self.value.encode("ascii"))

    @classmethod
    def create(cls, name: str, value: str) -> Header:
        """
        Creates a Header object as follows:  first name is used to find a corresponding
        Header subclass.  If no match, then Header is used.  Then the header value is parsed.
        If parsing succeeds, a Header object is returned.  If parsing fails, a ValueError
        is raised.
        """

        lname = name.lower()
        for subcls in cls.subclass_tree():
            if getattr(subcls, "name", "").lower() == lname:
                return cast(Header, subcls(value))
        else:
            return cls(name, value)

    @classmethod
    def subclass_tree(cls) -> Iterable[type[HeaderSubclass]]:
        """Generates subclass tree for cls."""
        for subcls in cls.__subclasses__():
            yield cast(type[HeaderSubclass], subcls)
            yield from subcls.subclass_tree()
