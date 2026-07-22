import pytest

from http_fields import UserAgent


def test_useragent_parse():
    value = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) "
        "Gecko/20100101 Firefox/42.0"
    )
    assert UserAgent.parse(value).value == value


@pytest.mark.parametrize(
    "value",
    [
        r"foo (a\) b)",
        r"foo (a\\b)",
        r"foo (a\(b)",
    ],
)
def test_useragent_comment_roundtrip_escapes(value: str):
    # Characters unescaped from quoted-pairs must be re-escaped on serialization,
    # so the output stays parseable (regression: bug 6).
    ua = UserAgent.parse(value)
    assert ua.value == value
    assert UserAgent.parse(ua.value) == ua


def test_useragent_invalid():
    with pytest.raises(ValueError):
        # https://jira.atlassian.com/browse/JRACLOUD-67600
        UserAgent.parse(
            "Atlassian HttpClient unknown / JIRA-1001.0.0-SNAPSHOT (100059) / Default"
        )
