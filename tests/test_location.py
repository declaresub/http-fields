from http_headers import Location


def test_location_from_value():
    value = "https://www.example.com/test"
    location = Location(value)
    assert location.uri == value
    assert location.value == value
