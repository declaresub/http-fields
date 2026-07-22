"""Property-based tests for the hand-rolled Structured Fields codec (RFC 9651).

Unlike the header grammars, structuredfields.py does not defer to abnf for the
serialize direction (regex/char-range/bounds validation) nor for value decode/encode
(base64, dates, string escaping, display-string %-coding). These properties fuzz that
hand-rolled code: encode<->decode symmetry (round-trip) and no-unexpected-crash.
"""

from datetime import datetime, timezone
from decimal import Decimal

from abnf import ParseError
from hypothesis import given, settings
from hypothesis import strategies as st

from http_headers.structuredfields import (
    DisplayString,
    InnerList,
    Item,
    Token,
    parse_dictionary,
    parse_item,
    parse_list,
    serialize_bare,
    serialize_dictionary,
    serialize_item,
    serialize_list,
)

_INTEGER_MAX = 10**15 - 1

# --- strategies for the bare-item types, each bounded to what SF can represent -------------

sf_integers = st.integers(min_value=-_INTEGER_MAX, max_value=_INTEGER_MAX)
# SF decimals: <= 12 integer digits and <= 3 fractional digits.
sf_decimals = st.decimals(
    min_value=Decimal("-999999999999.999"),
    max_value=Decimal("999999999999.999"),
    places=3,
    allow_nan=False,
    allow_infinity=False,
)
sf_booleans = st.booleans()
sf_bytes = st.binary(max_size=32)
# SF dates round-trip only to integer-second UTC; bound to a portable timestamp range.
sf_datetimes = st.integers(min_value=0, max_value=2**32).map(
    lambda ts: datetime.fromtimestamp(ts, tz=timezone.utc)
)
# SF strings: any %x20-7E char (serialize escapes \ and ").
sf_strings = st.text(alphabet=st.characters(min_codepoint=0x20, max_codepoint=0x7E))
# SF tokens: tchar-ish, must start with ALPHA / "*".
sf_tokens = st.from_regex(
    r"\A[A-Za-z*][A-Za-z0-9!#$%&'*+\-.^_`|~:/]*\Z"
).map(Token)
# SF display strings: arbitrary Unicode, minus lone surrogates (not UTF-8 encodable).
sf_display_strings = st.text(
    alphabet=st.characters(exclude_categories=("Cs",))
).map(DisplayString)

bare_items = st.one_of(
    sf_integers,
    sf_decimals,
    sf_booleans,
    sf_bytes,
    sf_datetimes,
    sf_strings,
    sf_tokens,
    sf_display_strings,
)

sf_keys = st.from_regex(r"\A[a-z*][a-z0-9_.*-]*\Z")

# Parameters: an ordered map of key -> bare item (dedup keys so round-trip is exact).
parameters = st.dictionaries(sf_keys, bare_items, max_size=4).map(
    lambda d: tuple(d.items())
)

items = st.builds(Item, bare_items, parameters)
inner_lists = st.builds(
    InnerList, st.lists(items, max_size=3).map(tuple), parameters
)
members = st.one_of(items, inner_lists)

sf_lists = st.lists(members, max_size=4).map(tuple)
sf_dictionaries = st.dictionaries(sf_keys, members, max_size=4).map(
    lambda d: tuple(d.items())
)


# --- round-trip: serialize then parse reconstructs an equal value -------------------------


@settings(max_examples=400, deadline=None)
@given(items)
def test_item_roundtrip(item: Item) -> None:
    assert parse_item(serialize_item(item)) == item


@settings(max_examples=300, deadline=None)
@given(sf_lists)
def test_list_roundtrip(value: tuple[object, ...]) -> None:
    assert parse_list(serialize_list(value)) == value


@settings(max_examples=300, deadline=None)
@given(sf_dictionaries)
def test_dictionary_roundtrip(value: tuple[tuple[str, object], ...]) -> None:
    assert parse_dictionary(serialize_dictionary(value)) == value


# --- no unexpected crash: the hand-rolled serializer only succeeds or raises Value/TypeError


# Lone surrogates are not UTF-8 encodable; the serializer must still fail in the
# ValueError family (UnicodeEncodeError is a ValueError subclass), never escape.
_surrogates = st.text(
    st.characters(min_codepoint=0xD800, max_codepoint=0xDFFF), min_size=1
)


@settings(max_examples=500, deadline=None)
@given(
    st.one_of(
        bare_items,
        # deliberately-invalid inputs the serializer must reject cleanly
        st.none(),
        st.floats(),
        st.lists(st.integers()),
        st.text().map(Token),  # tokens with illegal chars
        st.text().map(DisplayString),  # display strings incl. surrogates
        st.text(),  # strings incl. chars outside %x20-7E
        _surrogates.map(DisplayString),  # display strings with lone surrogates
        _surrogates,  # strings with lone surrogates
    )
)
def test_serialize_bare_no_unexpected_crash(value: object) -> None:
    try:
        result = serialize_bare(value)
    except (ValueError, TypeError):
        return
    assert isinstance(result, str)


# --- no unexpected crash: parsing arbitrary text only raises the grammar/value errors ------


@settings(max_examples=300, deadline=None)
@given(st.text(max_size=64))
def test_parse_no_unexpected_crash(text: str) -> None:
    for parse in (parse_item, parse_list, parse_dictionary):
        try:
            parse(text)
        except (ParseError, ValueError):
            pass
