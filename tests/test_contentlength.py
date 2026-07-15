import pytest

from http_headers.contentlength import ContentLength
from http_headers.parsedobjs import NonNegativeInt


def test_content_length_parse():
    header = ContentLength.parse("43")
    assert header.length == 43
    assert header.value == "43"


def test_content_length_from_int():
    header = ContentLength(43)
    assert header.length == 43
    assert isinstance(header.length, NonNegativeInt)
    assert header.value == "43"


def test_content_length_bad_length():
    with pytest.raises(ValueError):
        ContentLength(-1)


def test_content_length_wrong_type():
    with pytest.raises(TypeError):
        ContentLength(None)  # type: ignore[arg-type]
