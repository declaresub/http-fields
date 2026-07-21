import pytest

from http_headers import ContentDisposition, ExtValue


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            r"Attachment; filename=example.html",
            ContentDisposition.build(
                disposition_type="Attachment",
                disposition_parms={"filename": "example.html"},
            ),
        ),
        (
            r'INLINE; FILENAME="an example.html"',
            ContentDisposition.build(
                disposition_type="inline",
                disposition_parms={"FILENAME": "an example.html"},
            ),
        ),
        (
            r"attachment; filename*=UTF-8''%e2%82%ac%20rates",
            ContentDisposition.build(
                disposition_type="attachment",
                disposition_parms={
                    "filename*": ExtValue(charset="UTF-8", language="", value="€ rates")
                },
            ),
        ),
        (
            r"attachment; filename*=UTF-8'en'%e2%82%ac%20rates",
            ContentDisposition.build(
                disposition_type="attachment",
                disposition_parms={
                    "filename*": ExtValue(
                        charset="UTF-8", language="en", value="€ rates"
                    )
                },
            ),
        ),
        (
            r"notification",
            ContentDisposition.build(
                disposition_type="notification", disposition_parms={}
            ),
        ),
        (
            r"notification; foo=bar",
            ContentDisposition.build(
                disposition_type="notification", disposition_parms={"foo": "bar"}
            ),
        ),
        (
            r'notification; foo="bar\\baz"',
            ContentDisposition.build(
                disposition_type="notification",
                disposition_parms={"foo": "bar\\baz"},
            ),
        ),
        (
            r"test; foo*=utf-8''%E2%88%ABar",
            ContentDisposition.build(
                disposition_type="test",
                disposition_parms={"foo*": ExtValue(value="∫ar")},
            ),
        ),
    ],
)
def test_contentdisposition_parse(value: str, expected: ContentDisposition):
    assert ContentDisposition.parse(value) == expected


def test_contentdisposition_missing_type():
    with pytest.raises(TypeError):
        ContentDisposition.build()  # type: ignore[call-arg]


def test_contentdisposition_ext_parm_serializes():
    # A non-filename ext parameter must serialize to a valid header, not a
    # dataclass repr (regression: bug 4).
    cd = ContentDisposition.parse("attachment; foo=bar")
    assert cd.value == "attachment;foo=bar"
    # round-trips back to an equal object
    assert ContentDisposition.parse(cd.value) == cd


def test_contentdisposition_ext_value_decoded_once():
    # A literal percent (%25) in an ext-value must survive one decode, not two
    # (regression: bug 5).
    cd = ContentDisposition.parse("attachment; filename*=UTF-8''%2541.txt")
    parm_value = cd.disposition_parms[0].value
    assert isinstance(parm_value, ExtValue)
    assert parm_value.value == "%41.txt"


def test_contentdisposition_ext_value_encodes_slash():
    # "/" is not an RFC 5987 attr-char, so it must be percent-encoded; the result
    # must round-trip through the parser (regression: bug 23).
    cd = ContentDisposition.build("attachment", {"filename*": ExtValue(value="a/b.txt")})
    assert "/b.txt" not in cd.value
    assert ContentDisposition.parse(cd.value) == cd
