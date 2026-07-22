from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from abnf import Node, NodeVisitor
from abnf.grammars import rfc6266

from http_fields.parsedobjs import CaselessMixin, ParsedStr
from http_fields.visitors.rfc7230 import (
    QuotedString,
    QuotedStringVisitor,
    Token,
    TokenVisitor,
)


class DispositionType(CaselessMixin, ParsedStr):
    parser = rfc6266.Rule("disposition-type")


class DispositionTypeVisitor(NodeVisitor):
    @staticmethod
    def visit_disposition_type(node: Node):
        return DispositionType(node.value, parse=False)


class ValueVisitor(NodeVisitor):
    visit_quoted_string = QuotedStringVisitor()
    visit_token = TokenVisitor()

    def visit_value(self, node: Node) -> str:
        return next(filter(None, map(self.visit, node.children)))


def NotNone(x: Any) -> bool:
    return x is not None


@dataclass(frozen=True, kw_only=True)
class ExtValue:
    charset: str = "utf-8"
    language: str = ""
    value: str

    def parm_value(self) -> str:
        # quote() defaults to safe="/", but "/" is not an RFC 5987 attr-char and
        # must be percent-encoded; pass safe="" so nothing is left unencoded.
        encoded = quote(self.value, safe="", encoding=self.charset)
        return f"{self.charset}'{self.language}'{encoded}"

    def __str__(self):
        return self.parm_value()


class ExtValueVisitor(NodeVisitor):
    def visit_ext_value(self, node: Node) -> ExtValue:
        items = list(filter(NotNone, map(self.visit, node.children)))
        charset = items[0]
        language = items[1] if len(items) == 3 else ""
        # value_chars is already the fully pct-decoded byte string (visit_value_chars
        # resolves pct-encoded octets); decode it once. Passing it through unquote a
        # second time would re-decode any literal '%' the value legitimately contains.
        value_chars = items[-1]
        return ExtValue(
            charset=charset,
            language=language,
            value=value_chars.decode(charset),
        )

    @staticmethod
    def visit_charset(node: Node) -> str:
        return node.value

    @staticmethod
    def visit_language(node: Node) -> str:
        return node.value

    @staticmethod
    def visit_hexdig(node: Node) -> str:
        return node.value

    def visit_pct_encoded(self, node: Node) -> int:
        hex = "".join(filter(None, map(self.visit, node.children)))
        return int(hex, base=16)

    @staticmethod
    def visit_attr_char(node: Node) -> int:
        return ord(node.value)

    def visit_value_chars(self, node: Node) -> bytes:
        return bytes(list(filter(None, map(self.visit, node.children))))


class Filename(CaselessMixin, str):
    """The filename parm names 'filename', 'filename*' are case-insenstive.  I tripped over this
    once too often while testing, hence a class that removes the obstacle."""

    def __new__(cls, s: Any, parse: bool = True):
        if isinstance(s, cls):
            return s
        else:
            # if s can't be converted to str, this should fail.
            _s = str(s)
            if _s.lower() not in {"filename", "filename*"}:
                raise ValueError("Value must be 'filename' or 'filename*'.modulo case.")
            return super().__new__(cls, _s)

    def __repr__(self):
        return f"{self.__class__.__name__}({str.__repr__(str(self))})"


@dataclass(frozen=True)
class FilenameParm:
    name: Filename
    value: Token | QuotedString | ExtValue

    def __init__(self, name: str, value: str | ExtValue):
        object.__setattr__(self, "name", Filename(name))
        if name[-1] == "*":
            object.__setattr__(
                self,
                "value",
                value if isinstance(value, ExtValue) else ExtValue(value=value),
            )
        else:
            if not isinstance(value, str):
                raise TypeError('value associated to "filename" must be a str.')
            try:
                object.__setattr__(self, "value", Token(value))
            except ValueError:
                try:
                    object.__setattr__(self, "value", QuotedString(value))
                except ValueError as exc:
                    raise ValueError(
                        f"Value {value} could not be parsed as a Token or QuotedString."
                    ) from exc

    def __str__(self):
        return f"{self.name}={self.value}"


class FilenameParmNodeVisitor(NodeVisitor):
    visit_value = ValueVisitor()
    visit_ext_value = ExtValueVisitor()

    @staticmethod
    def visit_literal(node: Node):
        return node.value if node.value.lower() in {"filename", "filename*"} else None

    def visit_filename_parm(self, node: Node):
        assert len(node.children) == 3
        filename = Filename(self.visit_literal(node.children[0]))
        assert node.children[1].value == "="
        if filename == "filename":
            value = self.visit_value(node.children[2])
        else:
            value = self.visit_ext_value(node.children[2])
        return FilenameParm(filename, value)


@dataclass(frozen=True)
class DispExtParm:
    name: Token
    value: Token | QuotedString | ExtValue

    def __init__(self, name: str, value: str | ExtValue):
        object.__setattr__(self, "name", Token(name))
        if name[-1] == "*":
            if isinstance(value, ExtValue):
                object.__setattr__(self, "value", value)
            else:
                object.__setattr__(self, "value", ExtValue(value=value))
        else:
            if isinstance(value, str):
                try:
                    object.__setattr__(self, "value", Token(value))
                except ValueError:
                    try:
                        object.__setattr__(self, "value", QuotedString(value))
                    except ValueError as exc:
                        raise ValueError(
                            f'Unable to parse "{value}" as a Token or QuotedString.'
                        ) from exc
            else:
                raise TypeError(
                    f"Value for name {name} must be a string that parses as a "
                    "Token or QuotedString."
                )

    def __str__(self):
        return f"{self.name}={self.value}"


class DispExtParmVisitor(NodeVisitor):
    visit_token = TokenVisitor()
    visit_value = ValueVisitor()
    visit_ext_value = ExtValueVisitor()

    def visit_disp_ext_parm(self, node: Node):
        assert len(node.children) == 3
        name = self.visit_token(node.children[0])
        assert node.children[1].value == "="
        # the RFC 6266 grammar is ambiguous here. The rule 'token' matches everything matched
        # by 'ext-token', and the same is true for 'value' and 'ext-value'.  Thus we have to
        # disambiguate here by checking the name for a trailing '*', which marks an ext-thing.
        # In the case of an ext-name, we reparse the captured value as an ext-value.
        if name[-1] == "*" and node.children[2].name == "value":
            src = node.children[2].value
            ext_node = rfc6266.Rule("ext-value").parse_all(src)
            value = self.visit_ext_value(ext_node)
        else:
            value = self.visit(node.children[2])
        assert value
        return DispExtParm(name, value)


class DispositionParmNodeVisitor(NodeVisitor):
    visit_filename_parm = FilenameParmNodeVisitor()
    visit_disp_ext_parm = DispExtParmVisitor()

    def visit_disposition_parm(self, node: Node) -> tuple[str, str | ExtValue]:
        parm = next(filter(None, map(self.visit, node.children)))
        return parm


class ContentDispositionNodeVisitor(NodeVisitor):
    visit_disposition_type = DispositionTypeVisitor()
    visit_disposition_parm = DispositionParmNodeVisitor()

    def visit_content_disposition(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        disposition_type: DispositionType = next(items)
        disposition_parms: list[FilenameParm | DispExtParm] = [item for item in items]
        return disposition_type, disposition_parms
