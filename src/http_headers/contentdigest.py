"""Content-Digest and Repr-Digest header classes."""

from typing import ClassVar

from http_headers.structuredheaders import DigestHeader


class ContentDigest(DigestHeader):
    """Content-Digest header, as defined by RFC 9530: a Dictionary of algorithm name to the
    byte-sequence digest of the message content."""

    name: ClassVar[str] = "content-digest"


class ReprDigest(DigestHeader):
    """Repr-Digest header, as defined by RFC 9530: like Content-Digest, but over the selected
    representation."""

    name: ClassVar[str] = "repr-digest"
