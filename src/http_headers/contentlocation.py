"""Content-Location header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.uriheader import UriHeader


class ContentLocation(UriHeader):
    """Content-Location header, as defined by RFC 9110."""

    name: ClassVar[str] = "content-location"
    rule: ClassVar[Rule] = rfc9110.Rule("Content-Location")
