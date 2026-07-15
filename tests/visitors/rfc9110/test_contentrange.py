import pytest
from abnf.grammars import rfc9110

from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9110.contentrange import (
    ContentRangeVisitor,
    RangeResp,
    UnsatisfiedRange,
)
from http_headers.visitors.rfc9110.rangeunit import RangeUnit


@pytest.mark.parametrize(
    "src, expected",
    [
        (
            "bytes 42-1233/1234",
            (
                RangeUnit("bytes"),
                RangeResp(
                    NonNegativeInt(42), NonNegativeInt(1233), NonNegativeInt(1234)
                ),
            ),
        ),
        (
            "bytes 42-1233/*",
            (
                RangeUnit("bytes"),
                RangeResp(NonNegativeInt(42), NonNegativeInt(1233), None),
            ),
        ),
        ("bytes */1234", (RangeUnit("bytes"), UnsatisfiedRange(NonNegativeInt(1234)))),
    ],
)
def test_visitcontenttange(
    src: str, expected: tuple[RangeUnit, RangeResp | UnsatisfiedRange]
):
    node = rfc9110.Rule("Content-Range").parse_all(src)
    visitor = ContentRangeVisitor()
    assert visitor.visit(node) == expected
