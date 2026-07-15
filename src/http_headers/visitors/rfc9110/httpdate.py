from datetime import date, datetime, time, timezone
from typing import Any

from abnf import Node, NodeVisitor


class MonthVisitor(NodeVisitor):
    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    def visit_month(self, node: Node) -> int:
        return self.months[node.value]


class DayVisitor(NodeVisitor):
    def visit_day(self, node: Node) -> int:
        return int(node.value)


class YearVisitor(NodeVisitor):
    def visit_year(self, node: Node) -> int:
        return int(node.value)


class Date1Visitor(NodeVisitor):
    visit_month = MonthVisitor()
    visit_day = DayVisitor()
    visit_year = YearVisitor()

    def visit_date1(self, node: Node) -> date:
        day: int
        month: int
        year: int
        day, month, year = filter(None, map(self.visit, node.children))
        return date(year=year, month=month, day=day)


class Date2Visitor(NodeVisitor):
    visit_day = DayVisitor()
    visit_month = MonthVisitor()

    def visit_date2(self, node: Node) -> date:
        day: int
        month: int
        digit1: str
        digit2: str
        day, month, digit1, digit2 = filter(None, map(self.visit, node.children))
        year = int("20" + digit1 + digit2)
        date2 = date(year=year, month=month, day=day)

        # From RFC 2616 <https://tools.ietf.org/html/rfc2616#section-19.3>:
        #
        # "HTTP/1.1 clients and caches SHOULD assume that an RFC-850 date
        # which appears to be more than 50 years in the future is in fact
        # in the past (this helps solve the "year 2000" problem).
        #
        # So, on the off chance that we are parsing and RFC 850 date, we'll use this
        # suggestion to resolve the 2-digit date.

        today = datetime.utcnow().date()
        if date2 > today.replace(year=today.year + 50):
            date2 = date2.replace(year=date2.year - 100)
        return date2

    @staticmethod
    def visit_digit(node: Node) -> str:
        return node.value


class Date3Visitor(NodeVisitor):
    visit_month = MonthVisitor()

    def visit_date3(self, node: Node) -> tuple[int, int]:
        values: list[Any] = list(filter(None, map(self.visit, node.children)))
        month: int = values[0]
        day = int("".join(values[1:]))
        return month, day

    @staticmethod
    def visit_digit(node: Node) -> str:
        return node.value


class TimeOfDayVisitor(NodeVisitor):
    def visit_time_of_day(self, node: Node) -> time:
        hour, minute, second = filter(
            lambda x: x is not None, map(self.visit, node.children)
        )
        return time(hour=hour, minute=minute, second=second)

    def visit_hour(self, node: Node) -> int:
        return int(node.value)

    def visit_minute(self, node: Node) -> int:
        return int(node.value)

    def visit_second(self, node: Node) -> int:
        return int(node.value)


class IMfFixDateVisitor(NodeVisitor):
    visit_date1 = Date1Visitor()
    visit_time_of_day = TimeOfDayVisitor()

    def visit_imf_fixdate(self, node: Node) -> datetime:
        date_: date
        time_of_day: time
        date_, time_of_day = filter(None, map(self.visit, node.children))
        return datetime.combine(date=date_, time=time_of_day).replace(
            tzinfo=timezone.utc
        )


class RFC850DateVisitor(NodeVisitor):
    visit_date2 = Date2Visitor()
    visit_time_of_day = TimeOfDayVisitor()

    def visit_rfc850_date(self, node: Node) -> datetime:
        date_: date
        time_of_day: time
        date_, time_of_day = filter(None, map(self.visit, node.children))
        return datetime.combine(date=date_, time=time_of_day).replace(
            tzinfo=timezone.utc
        )


class AscTimeDateVisitor(NodeVisitor):
    visit_date3 = Date3Visitor()
    visit_time_of_day = TimeOfDayVisitor()
    visit_year = YearVisitor()

    def visit_asctime_date(self, node: Node) -> datetime:
        date3: tuple[int, int]
        time_of_day: time
        year: int
        date3, time_of_day, year = filter(None, map(self.visit, node.children))
        return datetime.combine(
            date(year=year, month=date3[0], day=date3[1]), time=time_of_day
        ).replace(tzinfo=timezone.utc)


class ObsDateVisitor(NodeVisitor):
    visit_rfc850_date = RFC850DateVisitor()
    visit_asctime_date = AscTimeDateVisitor()

    def visit_obs_date(self, node: Node):
        return next(filter(None, map(self.visit, node.children)))


class HttpDateVisitor(NodeVisitor):
    visit_imf_fixdate = IMfFixDateVisitor()
    visit_obs_date = ObsDateVisitor()

    def visit_http_date(self, node: Node) -> datetime:
        return next(filter(None, map(self.visit, node.children)))
