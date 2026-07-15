from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.parameters as parameters
import http_headers.visitors.rfc9110.token as token
import http_headers.visitors.rfc9110.type as type


@dataclass(frozen=True)
class MediaType:
    type: token.Token
    subtype: token.Token
    params: tuple[parameters.Parameter, ...]

    def __init__(
        self,
        type: str,
        subtype: str,
        params: "list[parameters.Parameter] | tuple[parameters.Parameter, ...] | None" = None,
    ):
        object.__setattr__(self, "type", token.Token(type))
        object.__setattr__(self, "subtype", token.Token(subtype))
        object.__setattr__(self, "params", tuple(params) if params else ())

    def __str__(self) -> str:
        return f"{self.type}/{self.subtype}" + (
            (";" + ";".join(str(p) for p in self.params)) if self.params else ""
        )


class MediaTypeVisitor(NodeVisitor):
    visit_type = type.TypeVisitor()
    visit_subtype = type.SubtypeVisitor()
    visit_parameters = parameters.ParametersVisitor()

    def visit_media_type(self, node: Node) -> MediaType:
        items = filter(None, map(self.visit, node.children))
        type = next(items)
        subtype = next(items)
        params: list[parameters.Parameter] = next(items, [])
        return MediaType(type, subtype, params)


class ContentTypeVisitor(NodeVisitor):
    visit_media_type = MediaTypeVisitor()

    def visit_content_type(self, node: Node):
        return next(filter(None, map(self.visit, node.children)))
