from http_fields import EntityTag, IfNoneMatch


def test_ifnonematch_parse_star():
    assert IfNoneMatch.parse("*") == IfNoneMatch(wildcard=True)


def test_ifnonematch_parse_tag():
    assert IfNoneMatch.parse('"deadbeef"') == IfNoneMatch(EntityTag("deadbeef"))


def test_ifnonematch_matches():
    header = IfNoneMatch(EntityTag("deadbeef"), EntityTag("test"))
    assert header.matches(EntityTag("foo"))


def test_ifnonematch_matches_none():
    assert not IfNoneMatch(wildcard=True).matches(EntityTag("test"))
