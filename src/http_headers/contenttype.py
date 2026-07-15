"""ContentType header class"""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import ContentTypeVisitor, MediaType, Parameter


class ContentType(Header):
    """Content-Type header."""

    name = "Content-Type"

    def __init__(
        self,
        value: str | None = None,
        *,
        type: str | None = None,
        subtype: str | None = None,
        charset: str | None = None,
        boundary: str | None = None,
        params: list[tuple[str, str]] | None = None,
    ):
        """
        Usage:
         header = ContentType("text/html; charset=utf-8")
         header = ContentType(type="text", subtype="html", params=[('charset', 'utf-8')]

         Use the first version to create a ContentType from header value, or because it is simple.
         Use the second version to create a ContentType from pieces.  Arguments are parsed using the grammar.
        """

        if isinstance(value, str):
            self.value = value
        else:
            if not isinstance(type, str):
                raise TypeError("If value is None, then type must be str.")
            if not isinstance(subtype, str):
                raise TypeError("If value is None, then subtype must be str.")

            all_params: list[Parameter] = [
                p
                for p in [
                    Parameter("charset", charset) if charset else None,
                    Parameter("boundary", boundary) if boundary else None,
                ]
                if p
            ]
            for p in params if params else []:
                param = Parameter(*p)
                if param.name == "charset" and charset:
                    continue
                elif param.name == "boundary" and boundary:
                    continue
                else:
                    all_params.append(param)
            self._media_type = MediaType(type, subtype, all_params)

    @property
    def type(self) -> str:
        return self._media_type.type

    @property
    def subtype(self) -> str:
        return self._media_type.subtype

    @property
    def params(self) -> list[Parameter]:
        return list(self._media_type.params)

    @property
    def charset(self) -> str | None:
        for param in self._media_type.params:
            if param.name == "charset":
                return param.value
        else:
            return None

    @property
    def boundary(self) -> str | None:
        for param in self._media_type.params:
            if param.name.lower() == "boundary":
                return param.value
        else:
            return None

    @property
    def value(self) -> str:
        return str(self._media_type)

    @value.setter
    def value(self, val: str):
        rule = rfc9110.Rule("Content-Type")
        node = rule.parse_all(val)
        visitor = ContentTypeVisitor()
        self._media_type: MediaType = visitor.visit(node)

    def __eq__(self, __o: object) -> bool:
        return (
            self._media_type == __o._media_type
            if isinstance(__o, self.__class__)
            else NotImplemented
        )
