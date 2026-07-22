"""Proxy-Status header class."""

from typing import ClassVar

from http_fields.structuredheaders import StructuredListHeader


class ProxyStatus(StructuredListHeader):
    """Proxy-Status header, as defined by RFC 9209. Each ``members`` item identifies an
    intermediary (its bare value) and carries parameters such as ``error`` and ``next-hop``."""

    name: ClassVar[str] = "proxy-status"
