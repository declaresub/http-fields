"""Location header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.uriheader import UriHeader


class Location(UriHeader):
    """Location header, as defined by RFC 9110."""

    name: ClassVar[str] = "Location"
    rule: ClassVar[Rule] = rfc9110.Rule("Location")
