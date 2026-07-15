"""RetryAfter header class."""

from datetime import datetime

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import RetryAfterVisitor, imf_fixdate


class RetryAfter(Header):
    """Retry-After header."""

    name = "Retry-After"

    def __init__(self, value: str | int | datetime):
        """
        Initializes a Retry-After header. At least one of delay_seconds, http_date must be
        supplied.

        :param delay_seconds: a non-negative integer.
        :param http_date: a datetime.datetime object.
        :returns: None
        """

        if isinstance(value, str):
            self.value = value
        elif isinstance(value, int):
            if value < 0:
                raise ValueError("delay_seconds argument must be non-negative.")
            self.delay = value
        elif isinstance(value, datetime):  # type: ignore
            self.delay = value
        else:
            raise TypeError("value must of type str, int, or datetime.")

    @property
    def value(self):
        if isinstance(self.delay, int):
            return str(self.delay)
        else:
            assert isinstance(self.delay, datetime)
            return imf_fixdate(self.delay)

    @value.setter
    def value(self, val: str):
        node = rfc9110.Rule("Retry-After").parse_all(val)
        visitor = RetryAfterVisitor()
        delay = visitor.visit(node)
        assert isinstance(delay, (int, datetime))
        self.delay = delay
