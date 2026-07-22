"""Content-Location header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_fields.parsedobjs import ParsedStr
from http_fields.uriheader import UriHeader


class ContentLocationUri(ParsedStr):
    """A Content-Location URI reference (RFC 9110). Self-validating."""

    parser = rfc9110.Rule("Content-Location")


class ContentLocation(UriHeader):
    """Content-Location header, as defined by RFC 9110."""

    name: ClassVar[str] = "content-location"
    rule: ClassVar[Rule] = rfc9110.Rule("Content-Location")
    uri_type: ClassVar[type[ParsedStr]] = ContentLocationUri
    uri: ContentLocationUri
