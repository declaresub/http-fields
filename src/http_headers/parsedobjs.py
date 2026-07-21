"""A few classes that parse or otherwise check values."""

from typing import Any

from abnf import ParseError, Rule


class ParsedStr(str):
    """str subclass that supports parsing at object creation. Subclasses of ParsedStr
    supply an abnf Rule used to parse the passed string."""

    parser: Rule

    def __new__(cls, s: Any, parse: bool = True):
        if isinstance(s, cls):
            return s
        else:
            # if s can't be converted to str, this should fail.
            _s = str(s)
            try:
                return super().__new__(
                    cls, cls.parser.parse_all(_s).value if parse else _s
                )
            except ParseError as exc:
                raise ValueError(f'Invalid {cls.parser.name} "{s}".') from exc

    def __repr__(self):
        return f"{self.__class__.__name__}({str.__repr__(str(self))})"


class CaselessMixin:
    """Used to define case-insensitive matching for str subclasses."""

    def __eq__(self, __o: object) -> bool:
        # comparison should be case-insensitive.
        return (
            self.casefold() == __o.casefold()
            if isinstance(self, str) and isinstance(__o, str)
            else NotImplemented
        )

    def __hash__(self) -> int:
        # and because we redefined __eq__, we need to redefine __hash__ for consistency.
        assert isinstance(self, str)
        return hash(self.casefold())


class NonNegativeInt(int):
    """Non-negative int type."""

    def __new__(cls, value: Any):
        if isinstance(value, cls):
            return value
        else:
            if isinstance(value, float) and not value.is_integer():
                # int(3.7) would silently truncate; reject non-integral input.
                raise ValueError("Value must be a whole number.")
            val = super().__new__(cls, value)
            if val >= 0:
                return val
            else:
                raise ValueError("Value must be non-negative.")
