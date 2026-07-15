import pytest
from abnf.grammars import rfc3986

from http_headers.visitors.rfc3986 import Scheme, SchemeVisitor


def test_scheme():
    scheme = Scheme("http")
    assert scheme == "http"


def test_scheme_scheme():
    scheme = Scheme("http")
    assert Scheme(scheme) is scheme


def test_scheme_invalid():
    with pytest.raises(ValueError):
        Scheme("http*")


def test_scheme_hash():
    scheme = Scheme("http")
    assert hash(scheme) == hash("http")


def test_visit_scheme():
    src = "http"
    node = rfc3986.Rule("scheme").parse_all(src)
    assert SchemeVisitor().visit(node) == Scheme("http")
