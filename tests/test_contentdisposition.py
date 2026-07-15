import pytest

from http_headers import ContentDisposition, ExtValue


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            r"Attachment; filename=example.html",
            ContentDisposition(
                disposition_type="Attachment",
                disposition_parms={"filename": "example.html"},
            ),
        ),
        (
            r'INLINE; FILENAME="an example.html"',
            ContentDisposition(
                disposition_type="inline",
                disposition_parms={"FILENAME": "an example.html"},
            ),
        ),
        (
            r"attachment; filename*=UTF-8''%e2%82%ac%20rates",
            ContentDisposition(
                disposition_type="attachment",
                disposition_parms={
                    "filename*": ExtValue(charset="UTF-8", language="", value="€ rates")
                },
            ),
        ),
        (
            r"attachment; filename*=UTF-8'en'%e2%82%ac%20rates",
            ContentDisposition(
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
            ContentDisposition(disposition_type="notification", disposition_parms={}),
        ),
        (
            r"notification; foo=bar",
            ContentDisposition(
                disposition_type="notification", disposition_parms={"foo": "bar"}
            ),
        ),
        (
            r'notification; foo="bar\\baz"',
            ContentDisposition(
                disposition_type="notification", disposition_parms={"foo": "bar\\baz"}
            ),
        ),
        (
            r"test; foo*=utf-8''%E2%88%ABar",
            ContentDisposition(
                disposition_type="test",
                disposition_parms={"foo*": ExtValue(value="∫ar")},
            ),
        ),
    ],
)
def test_accept_from_value(value: str, expected: ContentDisposition):
    print(expected)
    content_disposition = ContentDisposition(value)
    print(content_disposition)
    assert content_disposition == expected


def test_content_disposition_type_error():
    with pytest.raises(TypeError):
        ContentDisposition()
