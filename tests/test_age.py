from http_headers import Age, NonNegativeInt


def test_age_from_value():
    value = "111"
    header = Age(value)
    assert header.seconds == 111


def test_age_from_init():
    header = Age(seconds=111)
    assert isinstance(header.seconds, NonNegativeInt)
    assert header.seconds == 111


def test_age_value():
    header = Age(seconds=111)
    assert header.value == "111"
