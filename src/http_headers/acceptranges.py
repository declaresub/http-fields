from abnf import ParseError
from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AcceptRangesVisitor, FieldName, RangeUnit


class AcceptRanges(Header):
    name = FieldName("accept-ranges")
    parse = rfc9110.Rule("accept-ranges").parse_all
    visit = AcceptRangesVisitor().visit

    def __init__(self, *value: str):
        """Most of the time, value will be a single item 'bytes'. Less often, value will be 'None'.
        The grammar allows multiple values, though."""
        if len(value) == 1:
            self.value = value[0]
        else:
            self.range_units = [RangeUnit(v) for v in value]

    @property
    def value(self):
        """Returns header value."""
        return ",".join(str(item) for item in self.range_units)

    @value.setter
    def value(self, val: str):
        try:
            node = self.parse(val)
        except ParseError as exc:
            raise ValueError(f"Invalid {self.name} value.") from exc
        self.range_units: list[RangeUnit] = self.visit(node)
