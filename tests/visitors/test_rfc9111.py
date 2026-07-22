from datetime import datetime, timezone

from abnf.grammars import rfc9111

from http_fields.visitors.rfc9110 import QuotedString, Token
from http_fields.visitors.rfc9111 import (
    AgeVisitor,
    CacheDirective,
    CacheDirectiveVisitor,
    ExpiresVisitor,
)


def test_agevisitor():
    src = "23"
    node = rfc9111.Rule("age").parse_all(src)
    visitor = AgeVisitor()
    assert visitor.visit(node) == 23


def test_cachedirective_1():
    directive = CacheDirective("max-age", 1)
    assert isinstance(directive.name, Token)
    assert directive.name == "max-age"
    assert directive.value == 1


def test_cachedirective_2():
    directive = CacheDirective("must-revalidate")
    assert directive.name == "must-revalidate"
    assert directive.value is True


def test_cachedirective_3():
    directive = CacheDirective("private")
    assert directive.name == "private"
    assert directive.value is True


def test_cachedirective_4():
    directive = CacheDirective("no-cache", "Foo, Bar")
    assert directive.name == "no-cache"
    assert isinstance(directive.value, QuotedString)
    assert directive.value == '"Foo, Bar"'


def test_cachedirective_eq():
    assert CacheDirective("max-age", 1) == CacheDirective("max-age", 1)


def test_cachedirective_str():
    directive = CacheDirective("no-cache", "Foo, Bar")
    assert str(directive) == 'no-cache="Foo, Bar"'


def test_cachedirective_visitor():
    src = 'no-cache="Foo, Bar"'
    node = rfc9111.Rule("cache-directive").parse_all(src)
    directive = CacheDirectiveVisitor().visit(node)
    assert directive == CacheDirective("no-cache", "Foo, Bar")


def test_expires_visitor():
    src = "Tue, 03 Jan 2023 12:33:00 GMT"
    node = rfc9111.Rule("expires").parse_all(src)
    expire_time = ExpiresVisitor().visit(node)
    assert expire_time == datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc)
