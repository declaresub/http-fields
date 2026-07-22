from datetime import date, datetime, time, timezone

import pytest
from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.httpdate import (
    AscTimeDateVisitor,
    Date1Visitor,
    Date2Visitor,
    Date3Visitor,
    DayVisitor,
    HttpDateVisitor,
    IMfFixDateVisitor,
    MonthVisitor,
    ObsDateVisitor,
    RFC850DateVisitor,
    TimeOfDayVisitor,
    YearVisitor,
)


def test_month_visitor():
    src = "Apr"
    node = rfc9110.Rule("month").parse_all(src)
    assert MonthVisitor().visit(node) == 4


def test_day_visitor():
    src = "19"
    node = rfc9110.Rule("day").parse_all(src)
    assert DayVisitor().visit(node) == 19


def test_year_visitor():
    src = "2022"
    node = rfc9110.Rule("year").parse_all(src)
    assert YearVisitor().visit(node) == 2022


def test_date1_visitor():
    src = "01 Apr 2022"
    node = rfc9110.Rule("date1").parse_all(src)
    assert Date1Visitor().visit(node) == date(2022, 4, 1)


def test_date2_visitor():
    src = "01-Apr-99"
    node = rfc9110.Rule("date2").parse_all(src)
    assert Date2Visitor().visit(node) == date(1999, 4, 1)


def test_date3_visitor():
    src = "Apr  1"
    node = rfc9110.Rule("date3").parse_all(src)
    assert Date3Visitor().visit(node) == (4, 1)


def test_timeofday_visitor():
    src = "12:34:56"
    node = rfc9110.Rule("time-of-day").parse_all(src)
    assert TimeOfDayVisitor().visit(node) == time(12, 34, 56)


def test_imffixdate_visitor():
    src = "Tue, 03 Jan 2023 12:33:00 GMT"
    node = rfc9110.Rule("IMF-fixdate").parse_all(src)
    assert IMfFixDateVisitor().visit(node) == datetime(
        2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc
    )


def test_rfc850date_visitor():
    src = "Tuesday, 03-Jan-23 12:36:01 GMT"
    node = rfc9110.Rule("rfc850-date").parse_all(src)
    assert RFC850DateVisitor().visit(node) == datetime(
        2023, 1, 3, 12, 36, 1, tzinfo=timezone.utc
    )


def test_asctimedate_visitor():
    src = "Tue Jan 03 12:36:01 2023"
    node = rfc9110.Rule("asctime-date").parse_all(src)
    assert AscTimeDateVisitor().visit(node) == datetime(
        2023, 1, 3, 12, 36, 1, tzinfo=timezone.utc
    )


@pytest.mark.parametrize(
    "src, expected",
    [
        (
            "Tuesday, 03-Jan-23 12:36:01 GMT",
            datetime(2023, 1, 3, 12, 36, 1, tzinfo=timezone.utc),
        ),
        (
            "Tue Jan 03 12:36:01 2023",
            datetime(2023, 1, 3, 12, 36, 1, tzinfo=timezone.utc),
        ),
    ],
)
def test_obsdate_visitor(src: str, expected: datetime):
    node = rfc9110.Rule("obs-date").parse_all(src)
    assert ObsDateVisitor().visit(node) == expected


def test_http_date_visitor():
    src = "Tue, 03 Jan 2023 12:33:00 GMT"
    node = rfc9110.Rule("HTTP-date").parse_all(src)
    assert HttpDateVisitor().visit(node) == datetime(
        2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc
    )
