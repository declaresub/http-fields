from abnf.grammars import rfc9110

from http_headers.parsedobjs import CaselessMixin, ParsedStr


class FieldName(CaselessMixin, ParsedStr):
    """Represents an RFC 9110 field name."""

    parser = rfc9110.Rule("field-name")


class FieldValue(ParsedStr):
    """Represents an RFC 9110 field value."""

    parser = rfc9110.Rule("field-value")
