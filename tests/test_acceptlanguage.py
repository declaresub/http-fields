from http_fields import AcceptLanguage, WeightedLanguageRange


def test_acceptlanguage_parse():
    header = AcceptLanguage.parse("en-US, fr;q=0.5")
    assert header.language_ranges == (
        WeightedLanguageRange("en-US"),
        WeightedLanguageRange("fr", 0.5),
    )


def test_acceptlanguage_value():
    assert AcceptLanguage(("en-US", None), ("fr", 0.5)).value == "en-US, fr;q=0.5"


def test_acceptlanguage_wildcard_zero():
    # a q=0 range must be preserved (falsy-0 regression).
    assert AcceptLanguage(("*", 0)).value == "*;q=0"
