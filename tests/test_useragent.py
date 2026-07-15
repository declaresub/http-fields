import pytest

from http_headers import UserAgent


def test_useragent_parse():
    value = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) "
        "Gecko/20100101 Firefox/42.0"
    )
    assert UserAgent.parse(value).value == value


def test_useragent_invalid():
    with pytest.raises(ValueError):
        # https://jira.atlassian.com/browse/JRACLOUD-67600
        UserAgent.parse(
            "Atlassian HttpClient unknown / JIRA-1001.0.0-SNAPSHOT (100059) / Default"
        )
