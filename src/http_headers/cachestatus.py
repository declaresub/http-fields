"""Cache-Status header class."""

from typing import ClassVar

from http_headers.structuredheaders import StructuredListHeader


class CacheStatus(StructuredListHeader):
    """Cache-Status header, as defined by RFC 9211. Each ``members`` item identifies a cache
    (its bare value) and carries parameters such as ``hit``, ``fwd``, ``ttl``, and ``detail``."""

    name: ClassVar[str] = "cache-status"
