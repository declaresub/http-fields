import pytest

from http_headers.contentlength import ContentLength


@pytest.mark.parametrize(
    "value, expected",
    [
        ("43", 43),
        (43, 43),
    ],
)
def test_content_length(value: str | int, expected: int):
    header = ContentLength(value)
    assert header.length == expected
    assert header.value == str(expected)


def test_header_contentlength_bad_length():
    with pytest.raises(ValueError):
        ContentLength(-1)


def test_content_length_wrong_type():
    with pytest.raises(TypeError):
        ContentLength(None)  # type: ignore
