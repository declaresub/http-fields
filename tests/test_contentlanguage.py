from http_headers import ContentLanguage, Header, LanguageTag


def test_contentlanguage_parse():
    header = ContentLanguage.parse("en, de-DE")
    assert header.languages == (LanguageTag("en"), LanguageTag("de-DE"))


def test_contentlanguage_value():
    assert ContentLanguage(LanguageTag("en"), LanguageTag("de-DE")).value == "en, de-DE"


def test_contentlanguage_create():
    assert isinstance(Header.create("content-language", "fr"), ContentLanguage)
