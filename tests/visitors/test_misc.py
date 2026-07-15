import pytest
from abnf.grammars import rfc9110

from http_headers.parsedobjs import NonNegativeInt, ParsedStr


class ParsedStrTester(ParsedStr):
    parser = rfc9110.Rule("ALPHA")


def test_parsedstr_from_str():
    s = ParsedStrTester("x")
    assert isinstance(s, ParsedStrTester)
    assert repr(s) == "ParsedStrTester('x')"


def test_parsedstr_from_parsedstr():
    s = ParsedStrTester("x")
    s1 = ParsedStrTester(s)
    assert s is s1


def test_nonnegative_int():
    assert NonNegativeInt(1) == 1
    assert NonNegativeInt(NonNegativeInt(1)) == NonNegativeInt(1)


def test_nonnegative_int_valueerror():
    with pytest.raises(ValueError):
        NonNegativeInt(-2)
