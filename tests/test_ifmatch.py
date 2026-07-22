from http_fields import EntityTag, IfMatch


def test_ifmatch_parse_star():
    assert IfMatch.parse("*") == IfMatch(wildcard=True)


def test_ifmatch_parse_tag():
    assert IfMatch.parse('"deadbeef"') == IfMatch(EntityTag("deadbeef"))


def test_ifmatch_matches():
    header = IfMatch(EntityTag("deadbeef"), EntityTag("test"))
    assert header.matches(EntityTag("deadbeef"))


def test_ifmatch_matches_any():
    assert IfMatch(wildcard=True).matches(EntityTag("test"))
