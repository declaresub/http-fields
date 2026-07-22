from http_fields import Header, Priority


def test_priority_parse():
    header = Priority.parse("u=5, i")
    assert header.urgency == 5
    assert header.incremental is True


def test_priority_defaults():
    header = Priority.parse("")
    assert header.urgency == 3
    assert header.incremental is False


def test_priority_value_omits_defaults():
    assert Priority().value == ""
    assert Priority(5).value == "u=5"
    assert Priority(incremental=True).value == "i"
    assert Priority(0, True).value == "u=0, i"


def test_priority_ignores_out_of_range():
    # RFC 9218: an out-of-range urgency is ignored (falls back to the default).
    assert Priority.parse("u=9").urgency == 3


def test_priority_create():
    assert isinstance(Header.create("priority", "u=1"), Priority)
