from typing import Any

import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.accept import (
    AcceptType,
    AcceptVisitor,
    MediaRange,
    MediaRangeVisitor,
)
from http_headers.visitors.rfc9110.parameters import Parameter
from http_headers.visitors.rfc9110.weight import Weight


def test_mediarange_str():
    media_range = MediaRange("text", "plain", params=[Parameter("charset", "utf-8")])
    assert str(media_range) == "text/plain;charset=utf-8"


@pytest.mark.parametrize(
    "src, expected",
    [("*/*", MediaRange("*", "*")), ("text/plain", MediaRange("text", "plain"))],
)
def test_mediarangevisitor_visit(src: str, expected: MediaRange):
    node = rfc9110.Rule("media-range").parse_all(src)
    visitor = MediaRangeVisitor()
    media_range = visitor.visit_media_range(node)
    assert media_range == expected


@pytest.mark.parametrize(
    "accept_type, attrs",
    [
        (
            AcceptType("text", "plain"),
            dict(type="text", subtype="plain", params=[], weight=None),
        ),
        (
            AcceptType("text", "plain", weight=0.5),
            dict(type="text", subtype="plain", params=[], weight=Weight(0.5)),
        ),
        (
            AcceptType("text", "plain", params=[("foo", "bar")]),
            dict(
                type="text",
                subtype="plain",
                params=[Parameter("foo", "bar")],
                weight=None,
            ),
        ),
        (
            AcceptType("text", "plain", params=[("foo", "bar"), ("q", "0.3")]),
            dict(
                type="text",
                subtype="plain",
                params=[Parameter("foo", "bar")],
                weight=Weight(0.3),
            ),
        ),
    ],
)
def test_accepttype(accept_type: AcceptType, attrs: dict[str, Any]):
    assert all(
        getattr(accept_type, attr_name) == attrs[attr_name] for attr_name in attrs
    )


def test_accepttype_str():
    accept_type = AcceptType("text", "plain", params=[("foo", "bar"), ("q", "0.3")])
    assert str(accept_type) == "text/plain;foo=bar;q=0.3"


@pytest.mark.parametrize(
    "src, expected",
    [
        (
            "text/plain; charset=utf-8; q=0.3, text/xml;q=1",
            [
                AcceptType("text", "plain", params=[("charset", "utf-8")], weight=0.3),
                AcceptType("text", "xml", weight=1.0),
            ],
        ),
        ("", []),
        (
            "image/png, image/jpeg; q=1, image/*",
            [
                AcceptType("image", "png"),
                AcceptType("image", "jpeg", weight=1.0),
                AcceptType("image", "*"),
            ],
        ),
    ],
)
def test_accept_visitor(src: str, expected: list[AcceptType]):
    node = rfc9110.Rule("Accept").parse_all(src)
    visitor = AcceptVisitor()
    accept_types = visitor.visit(node)
    assert accept_types == expected
