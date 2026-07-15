import ipaddress
import itertools

from abnf import Node, NodeVisitor, ParseError
from abnf.grammars import rfc3986


class URI(str):
    """Represents an RFC 3986 URI or relative URI."""

    def __new__(cls, s: str, parse: bool = True):
        if isinstance(s, cls):
            return s
        else:
            try:
                return super().__new__(
                    cls, rfc3986.Rule("URI").parse_all(s).value if parse else s
                )
            except ParseError as exc:
                raise ValueError(f'Invalid token value "{s}".') from exc

    def pct_decoded(self):
        pass


class Scheme(str):
    """Represents an RFC 3986 URL scheme.
    Case normalization per RFC 3986 section 6.2.2.1 is performed."""

    def __new__(cls, s: str, parse: bool = True):
        if isinstance(s, cls):
            return s
        else:
            try:
                return super().__new__(
                    cls,
                    (rfc3986.Rule("scheme").parse_all(s).value if parse else s).lower(),
                )
            except ParseError as exc:
                raise ValueError(f'Invalid scheme value "{s}".') from exc

    def __eq__(self, __x: object) -> bool:
        # scheme comparison should be case-insensitive.
        if isinstance(__x, str):
            return self.casefold() == __x.casefold()
        else:
            return NotImplemented

    def __hash__(self) -> int:
        # and because we redefined __eq__, we need to redefine __hash__ for consistency.
        return hash(self.casefold())


class SchemeVisitor(NodeVisitor):
    def visit_scheme(self, node: Node):
        return Scheme(node.value, parse=False)


class PctEncodedVisitor(NodeVisitor):
    unreserved_chars = set(
        itertools.chain(
            range(48, 58),
            range(65, 91),
            range(97, 123),
            [ord(x) for x in ["-", ".", "_", "~"]],
        )
    )

    @staticmethod
    def visit_hex_digit(node: Node):
        # perform case normalization per RFC 3986 section 6.2.2.1,
        return node.value.upper()

    @staticmethod
    def visit_literal(node: Node):
        # node.value can only be "%", assuming correct parsing.
        return node.value

    def visit_pct_encoded(self, node: Node):
        # perform percent-encoding normalization per RFC 3986 section 6.2.2.2,
        pct_char = "".join(filter(None, map(self.visit, node.children)))
        code = int(pct_char[1:], 16)
        return chr(code) if code in self.unreserved_chars else pct_char


class UserInfo(str):
    def __new__(cls, s: str, parse: bool = True):
        if isinstance(s, cls):
            return s
        else:
            try:
                return super().__new__(
                    cls, rfc3986.Rule("userinfo").parse_all(s).value if parse else s
                )
            except ParseError as exc:
                raise ValueError(f'Invalid userinfo value "{s}".') from exc


class UserInfoVisitor(NodeVisitor):
    @staticmethod
    def visit_userinfo(node: Node):
        return UserInfo(node.value, parse=False)


class IPvFuture(str):
    def __new__(cls, s: str, parse: bool = True):
        if isinstance(s, cls):
            return s
        else:
            try:
                return super().__new__(
                    cls, rfc3986.Rule("IPvFuture").parse_all(s).value if parse else s
                )
            except ParseError as exc:
                raise ValueError(f'Invalid IPvFuture value "{s}".') from exc


class IPLiteralVisitor(NodeVisitor):
    def visit_ip_literal(self, node: Node) -> ipaddress.IPv6Address | IPvFuture:
        return next(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_ipv6address(node: Node):
        return ipaddress.IPv6Address(node.value)

    @staticmethod
    def visit_ipvfuture(node: Node):
        return IPvFuture(node.value, parse=False)


class IPv4AddressVisitor(NodeVisitor):
    @staticmethod
    def visit_ipv4address(node: Node):
        return ipaddress.IPv4Address(node.value)


class RegName(str):
    """Represents an RFC 3986 registered-name, more commonly known as hostname.
    Case normalization per RFC 3986 section 6.2.2.1 is performed."""

    def __new__(cls, s: str, parse: bool = True):
        if isinstance(s, cls):
            return s
        else:
            try:
                return super().__new__(
                    cls,
                    rfc3986.Rule("reg-name").parse_all(s).value.lower() if parse else s,
                )
            except ParseError as exc:
                raise ValueError(f'Invalid reg-name value "{s}".') from exc


class RegNameVisitor(NodeVisitor):
    visit_pct_encoded = PctEncodedVisitor()

    @staticmethod
    def visit_unreserved(node: Node):
        return node.value

    @staticmethod
    def visit_sub_delims(node: Node):
        return node.value

    def visit_reg_name(self, node: Node):
        value = "".join(filter(None, map(self.visit, node.children)))
        return RegName(value, parse=False)


class HostVisitor(NodeVisitor):
    visit_ip_literal = IPLiteralVisitor()
    visit_ipv4address = IPv4AddressVisitor()
    visit_regname = RegNameVisitor()

    def visit_host(
        self, node: Node
    ) -> ipaddress.IPv6Address | IPvFuture | ipaddress.IPv4Address | RegName:
        return next(filter(None, map(self.visit, node.children)))


class Authority:
    userinfo: UserInfo | None


class AuthorityVisitor(NodeVisitor):
    visit_userinfo = UserInfoVisitor()
    visit_host = HostVisitor()

    @staticmethod
    def visit_port(node: Node):
        return int(node.value)

    def visit_authority(self, node: Node):

        return next(filter(None, map(self.visit, node.children)))
