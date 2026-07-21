"""SetCookie header class."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from logging import Logger, getLogger
from typing import Any, ClassVar, Literal, cast

from abnf.grammars import rfc6265
from abnf.grammars.misc import load_grammar_rules
from abnf.parser import Node, NodeVisitor, ParseError, Rule
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import imf_fixdate

_LOGGER = getLogger(__name__)


@load_grammar_rules()
class CookieDate(Rule):
    grammar = [
        "cookie-date     = *delimiter date-token-list *delimiter",
        "date-token-list = date-token *( 1*delimiter date-token )",
        "date-token      = 1*non-delimiter",
        "delimiter       = %x09 / %x20-2F / %x3B-40 / %x5B-60 / %x7B-7E",
        'non-delimiter   = %x00-08 / %x0A-1F / DIGIT / ":" / ALPHA / %x7F-FF',
        "non-digit       = %x00-2F / %x3A-FF",
        "day-of-month    = 1*2DIGIT [ non-digit *OCTET ]",
        'month           = ( "jan" / "feb" / "mar" / "apr" / "may" / "jun" / "jul" / "aug" / "sep" / "oct" / "nov" / "dec" ) *OCTET',
        "year            = 2*4DIGIT [ non-digit *OCTET ]",
        "time            = hms-time [ non-digit *OCTET ]",
        'hms-time        = time-field ":" time-field ":" time-field',
        "time-field      = 1*2DIGIT",
    ]


class CookieDateVisitor(NodeVisitor):
    def visit_cookie_date(self, node: Node):
        found_time: time | None = None
        found_day_of_month: int | None = None
        found_month: int | None = None
        found_year: int | None = None
        date_tokens = next(filter(None, map(self.visit, node.children)))
        for date_token in date_tokens:
            try:
                node = CookieDate("time").parse_all(date_token)
            except ParseError:
                pass
            else:
                if not found_time:
                    found_time = self.visit_time(node)
                    continue

            try:
                node = CookieDate("day-of-month").parse_all(date_token)
            except ParseError:
                pass
            else:
                if not found_day_of_month:
                    found_day_of_month = self.visit_day_of_month(node)
                    continue
            try:
                node = CookieDate("month").parse_all(date_token)
            except ParseError:
                pass
            else:
                if not found_month:
                    found_month = self.visit_month(node)
                    continue

            try:
                node = CookieDate("year").parse_all(date_token)
            except ParseError:
                pass
            else:
                if not found_year:
                    found_year = self.visit_year(node)
                    continue

        if found_time is None:
            raise ValueError("No valid time found in cookie date.")
        if found_day_of_month is None:
            raise ValueError("No valid day of month found in cookie date.")
        if found_month is None:
            raise ValueError("No valid month found in cookie date.")
        if found_year is None:
            raise ValueError("No valid day of month found in cookie date.")

        return datetime.combine(
            date(found_year, found_month, found_day_of_month), found_time
        )

    def visit_date_token_list(self, node: Node) -> list[str]:
        return list(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_date_token(node: Node):
        return node.value

    def visit_time(self, node: Node) -> time:
        return self.visit(node.children[0])

    def visit_hms_time(self, node: Node):
        h: int
        m: int
        s: int
        # Select the time-field children by name; the ":" separators visit to
        # None, and a zero-valued field (e.g. "00") would be lost by a
        # truthiness filter.
        h, m, s = (
            self.visit(child)
            for child in node.children
            if child.name == "time-field"
        )
        # raises ValueError if h, m. s do not satisfy the same bounds as
        # as specified by parsing algorithm.
        return time(h, m, s, tzinfo=timezone.utc)

    @staticmethod
    def visit_time_field(node: Node):
        return int(node.value)

    @staticmethod
    def visit_day_of_month(node: Node):
        # grammar implies that int(node.value) should not throw.
        # bounds checking as specified by parsing algorithm happens later.
        day_of_month = int(node.value)
        if 1 <= day_of_month <= 31:
            return day_of_month
        else:
            raise ValueError("day of month is out of valid range [1, 31].")

    @staticmethod
    def visit_month(node: Node):
        # grammar specifies case-insensitive match.
        month_names = [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]
        return 1 + month_names.index(node.value.lower())

    @staticmethod
    def visit_year(node: Node):
        value = int(node.value)
        if 70 <= value <= 99:
            year = 1900 + value
        elif 0 <= value <= 69:
            year = 2000 + value
        else:
            year = value

        if year >= 1601:
            return year
        else:
            raise ValueError("year must be at least 1601.")


def parse_cookie_date(src: str) -> datetime:
    """
    RFC 6265 specifies an algorithm to parse a cookie date. The reason is to
    support interoperablility with servers that may not quite follow the grammar
    as specified in RFC 6265 section 4."""

    node = CookieDate("cookie-date").parse_all(src)
    visitor = CookieDateVisitor()
    return visitor.visit(node)


@dataclass(frozen=True, kw_only=True)
class SetCookie(Header):
    """Set-Cookie header, as defined by RFC 6265.

    Use :meth:`build` to construct (and validate) from pieces, or :meth:`parse` to parse a
    raw header value with the lenient RFC 6265 section 5 algorithm.
    """

    name: ClassVar[str] = "Set-Cookie"

    cookie_name: str
    cookie_value: str
    domain: str | None = None
    path: str | None = None
    expires: datetime | None = None
    max_age: int | None = None
    secure: bool = False
    http_only: bool = False
    # None means the origin did not set a SameSite attribute; it is not serialized.
    samesite: str | None = None
    extension: tuple[str, ...] = ()

    @classmethod
    def build(
        cls,
        cookie_name: str,
        cookie_value: str,
        *,
        domain: str | None = None,
        path: str | None = None,
        expires: datetime | None = None,
        max_age: int | None = None,
        secure: bool = False,
        http_only: bool = False,
        samesite: Literal["Strict", "Lax", "None"] | None = None,
        extension: list[str] | None = None,
    ) -> Self:
        """Build a validated Set-Cookie from its pieces."""
        if not isinstance(cookie_name, str):
            raise TypeError("cookie_name must be str.")
        if not isinstance(cookie_value, str):
            raise TypeError("cookie_value must be str.")
        try:
            cookie_name = rfc6265.Rule("cookie-name").parse_all(cookie_name).value
            cookie_value = rfc6265.Rule("cookie-value").parse_all(cookie_value).value
        except ParseError as exc:
            raise ValueError("Invalid argument value.") from exc
        if domain is not None:
            try:
                rfc6265.Rule("domain-value").parse_all(domain)
            except ParseError as exc:
                raise ValueError("Invalid domain value.") from exc
        if path is not None:
            try:
                rfc6265.Rule("path-value").parse_all(path)
            except ParseError as exc:
                raise ValueError("Invalid path value.") from exc
        if expires is not None and expires.year < 1601:
            raise ValueError("Expires year must be at least 1601.")
        # the RFC 6265 grammar requires max-age to be positive; this is almost universally
        # ignored, so we go with the crowd and clamp negatives to 0.
        normalized_max_age = 0 if max_age and max_age < 0 else max_age
        ext = (
            tuple(rfc6265.Rule("extension-av").parse_all(x).value for x in extension)
            if extension
            else ()
        )
        return cls(
            cookie_name=cookie_name,
            cookie_value=cookie_value,
            domain=domain,
            path=path,
            expires=expires,
            max_age=normalized_max_age,
            secure=secure,
            http_only=http_only,
            samesite=samesite,
            extension=ext,
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse a Set-Cookie value using the lenient RFC 6265 section 5 algorithm, which
        is more forgiving than the section 4 grammar for interoperability."""
        attrs = cls._parse_value(value)
        attrs["extension"] = tuple(attrs["extension"])
        return cls(**attrs)

    @property
    def value(self) -> str:
        header_value = [f"{self.cookie_name}={self.cookie_value}"]
        if self.domain is not None:
            header_value.append(f"Domain={self.domain}")
        if self.path is not None:
            header_value.append(f"Path={self.path}")
        if self.expires is not None:
            header_value.append(f"Expires={imf_fixdate(self.expires)}")
        if self.max_age is not None:
            header_value.append(f"Max-Age={self.max_age}")
        if self.samesite is not None:
            header_value.append(f"SameSite={self.samesite}")
        if self.secure or self.samesite == "None":
            header_value.append("Secure")
        if self.http_only:
            header_value.append("HttpOnly")
        if self.extension:
            header_value.append("; ".join(self.extension))

        return "; ".join(header_value)

    @staticmethod
    def default_path(request_path: str):
        if request_path:
            if request_path[0] == "/":
                cmps = request_path.split("/")[1:-1]
                return "/" + "/".join(x for x in cmps)
            else:
                return "/"
        else:
            return "/"

    def expiry_time(self, *, now: datetime | None = None):
        """expiry time is the datetime at which the cookie expires.  It is computed
        as specified in RFC 6265."""
        if self.max_age is not None:
            if self.max_age > 0:
                if now is None:
                    now = datetime.now(timezone.utc)
                return now + timedelta(seconds=self.max_age)
            else:
                return datetime.fromtimestamp(0, timezone.utc)
        elif self.expires is not None:
            return self.expires
        else:
            return None

    @staticmethod
    def _parse_value(src: str, *, log: Logger = _LOGGER) -> dict[str, Any]:
        cookie_attrs: dict[str, Any] = {}

        ctl_chars = {
            "\x1a",
            "\x04",
            "\x7f",
            "\x01",
            "\x1b",
            "\x15",
            "\x14",
            "\x1c",
            "\x03",
            "\x0f",
            "\x08",
            "\x00",
            "\r",
            "\x02",
            "\x06",
            "\x07",
            "\x16",
            "\x19",
            "\x1e",
            "\x11",
            "\x17",
            "\x1f",
            "\x0b",
            "\x10",
            "\x0e",
            "\x0c",
            "\x1d",
            "\x05",
            "\x18",
            "\n",
            "\x13",
            "\x12",
        }
        for idx, x in enumerate(src):
            if x in ctl_chars:
                raise ValueError(f"Illegal character in value at offset {idx}")

        name_value_pair, attribute_src = (
            _ if len(_ := src.split(";", 1)) == 2 else (_[0], "")
        )
        name_value_split = name_value_pair.split("=", 1)
        if len(name_value_split) != 2:
            # RFC 6265 section 5.2 step 2: a name-value pair lacking "=" causes
            # the entire set-cookie-string to be ignored.
            raise ValueError("Set-Cookie name-value pair lacks '='.")
        cookie_name, cookie_value = (x.strip(" \t") for x in name_value_split)
        if not cookie_name:
            # RFC 6265 section 5.2 step 5: an empty cookie-name is ignored.
            raise ValueError("Set-Cookie name is empty.")
        # if len(cookie_name) + len(cookie_value) > 4096: this test is contained in RFC 6265bis, a new draft.
        # raise ValueError("Cookie name-value pair exceeds 4096 characters.")

        cookie_attrs["cookie_name"] = cookie_name
        cookie_attrs["cookie_value"] = cookie_value
        cookie_attrs["extension"] = cast(list[str], [])

        for attr in [x for x in attribute_src.split(";") if x]:
            attr_name, attr_value = (
                _
                if len(_ := [x.strip(" \t") for x in attr.split("=", 1)]) == 2
                else (_[0], "")
            )
            # if len(attr_value) > 1024: this test is contained in RFC 6265bis, a new draft.
            # ignore. log?
            # continue
            matchname = attr_name.lower()
            if matchname == "expires":
                try:
                    cookie_attrs["expires"] = parse_cookie_date(attr_value)
                except ValueError:
                    log.info(f"Invalid Expires value {attr_value}.")
            elif matchname == "max-age":
                try:
                    cookie_attrs["max_age"] = int(attr_value)
                except ValueError:
                    # ignore.
                    log.info(f"Invalid Max-Age value {attr_value}.")
            elif matchname == "domain":
                # An empty Domain attribute-value carries no cookie-domain; ignore it.
                if attr_value:
                    cookie_attrs["domain"] = (
                        attr_value[1:] if attr_value.startswith(".") else attr_value
                    ).lower()
            elif matchname == "path":
                # when cookie path is '' or not an absolute path, the default path should be used for comparison.  But computation
                # of the default path depends on the request path.  We don't want to entangle parsing with the request,
                # so we leave it to the user to call default_path as needed.
                cookie_attrs["path"] = attr_value if attr_value.startswith("/") else None
            elif matchname == "secure":
                cookie_attrs["secure"] = True
            elif matchname == "httponly":
                cookie_attrs["http_only"] = True
            elif matchname == "samesite":
                # Store the canonical spelling; an unrecognized value is treated
                # as absent (None) so it is never serialized as "SameSite=Default".
                cookie_attrs["samesite"] = {
                    "strict": "Strict",
                    "lax": "Lax",
                    "none": "None",
                }.get(attr_value.lower())
            else:
                # extension-av
                # RFC 6256 Section 5 explicitly ignores extension-av in its loose parsing algorithm.
                # In the Set-Cookie grammar, attributes are delimited by ";" SP.  This algorithm
                # splits attributes on ";", then strips SP, TAB from attribute name, value.  But "SP" is a valid
                # attribute-av character, so we only strip the leading space, if present.
                cookie_attrs["extension"].append(attr[1:] if attr[0] == " " else attr)
        return cookie_attrs
