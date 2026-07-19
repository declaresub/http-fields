import base64

from http_headers import ContentDigest, Header, ReprDigest


def test_contentdigest_parse():
    digest = base64.b64encode(b"hello world").decode()
    header = ContentDigest.parse(f"sha-256=:{digest}:")
    assert header.digests == (("sha-256", b"hello world"),)
    assert header.value == f"sha-256=:{digest}:"


def test_contentdigest_multiple():
    header = ContentDigest.parse("sha-256=:AA==:, sha-512=:AA==:")
    assert [alg for alg, _ in header.digests] == ["sha-256", "sha-512"]


def test_reprdigest():
    header = ReprDigest(("sha-256", b"\x00\x01"))
    assert header.value == "sha-256=:AAE=:"
    assert ReprDigest.parse(header.value) == header


def test_digest_create():
    assert isinstance(Header.create("content-digest", "sha-256=:AA==:"), ContentDigest)
    assert isinstance(Header.create("repr-digest", "sha-256=:AA==:"), ReprDigest)
