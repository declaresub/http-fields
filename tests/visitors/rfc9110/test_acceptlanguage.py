from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.acceptlanguage import (
    AcceptLanguageVisitor,
    WeightedLanguageRange,
)


def test_acceptlanguagevisitor():
    src = "da, en-gb;q=0.8, en;q=0.7"
    node = rfc9110.Rule("Accept-Language").parse_all(src)
    visitor = AcceptLanguageVisitor()
    items = visitor.visit(node)
    expected = [
        WeightedLanguageRange("da"),
        WeightedLanguageRange("en-gb", 0.8),
        WeightedLanguageRange("en", 0.7),
    ]
    assert items == expected
