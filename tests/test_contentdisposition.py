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
