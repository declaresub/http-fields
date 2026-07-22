"""Referer header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.parsedobjs import ParsedStr
from http_headers.uriheader import UriHeader


class RefererUri(ParsedStr):
    """A Referer URI reference (RFC 9110). Self-validating."""

    parser = rfc9110.Rule("Referer")


class Referer(UriHeader):
    """Referer header, as defined by RFC 9110."""

    name: ClassVar[str] = "referer"
    rule: ClassVar[Rule] = rfc9110.Rule("Referer")
    uri_type: ClassVar[type[ParsedStr]] = RefererUri
    uri: RefererUri
