from datetime import datetime, timezone

import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110._base import imf_fixdate, transform


@pytest.mark.parametrize(
    "src, expected",
    [
        ([], []),
        (["a"], [("a", None)]),
        (["a", "b"], [("a", None), ("b", None)]),
        (["a", 1, "b"], [("a", 1), ("b", None)]),
    ],
)
def test_transform(src: list[str | int], expected: list[tuple[str, int | None]]):
    assert list(transform(iter(src), str, int)) == expected


def test_imf_fixdate():
    assert (
        imf_fixdate(datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc))
        == "Tue, 03 Jan 2023 12:33:00 GMT"
    )


def test_imf_fixdate_format():
    src = imf_fixdate(datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc))
    assert rfc9110.Rule("IMF-fixdate").parse_all(src)
