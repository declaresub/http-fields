from __future__ import annotations

from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110._base as base
import http_headers.visitors.rfc9110.parameters as parameters
import http_headers.visitors.rfc9110.token as token
import http_headers.visitors.rfc9110.type as type
import http_headers.visitors.rfc9110.weight as weight

Parameter = parameters.Parameter
ParametersVisitor = parameters.ParametersVisitor
SubtypeVisitor = type.SubtypeVisitor
Token = token.Token
TypeVisitor = type.TypeVisitor
Weight = weight.Weight
WeightVisitor = weight.WeightVisitor
as_qvalue = weight.as_qvalue


@dataclass(frozen=True)
class MediaRange:
    type: Token
    subtype: Token
    params: tuple[Parameter, ...]

    def __init__(self, type: str, subtype: str, params: list[Parameter] | None = None):
        object.__setattr__(self, "type", Token(type))
        object.__setattr__(self, "subtype", Token(subtype))
        object.__setattr__(self, "params", tuple(params) if params else ())

    def __str__(self) -> str:
        return f"{self.type}/{self.subtype}" + (
            (";" + ";".join(str(p) for p in self.params)) if self.params else ""
        )


class MediaRangeVisitor(NodeVisitor):
    visit_type = TypeVisitor()
    visit_subtype = SubtypeVisitor()
    visit_parameters = ParametersVisitor()

    def visit_media_range(self, node: Node) -> MediaRange:
        items = filter(None, map(self.visit, node.children))
        item = next(items)
        if item == "*/*":
            type, subtype = tuple([Token(x) for x in item.split("/")])
            # and anything else must be a param.
        else:
            type = item
            item = next(items)
            subtype = Token("*") if item == "/*" else item
        params: list[Parameter] = next(items, [])
        return MediaRange(type, subtype, params)

    @staticmethod
    def visit_literal(node: Node):
        return node.value if node.value in ["*/*", "/*"] else None


class AcceptType:
    def __init__(
        self,
        type: str,
        subtype: str,
        *,
        params: list[tuple[str, str] | Parameter] | None = None,
        weight: float | Weight | None = None,
    ):
        self.type = Token(type)
        self.subtype = Token(subtype)
        _params = (
            [Parameter(*p) if isinstance(p, tuple) else p for p in params]
            if params
            else []
        )
        if isinstance(weight, (float, Weight)):
            self.weight = Weight(qvalue=weight) if isinstance(weight, float) else weight
            self.params: tuple[Parameter, ...] = tuple(_params)
        else:
            # sometimes, weight was captured by parser as a parameter because abnf backtracking is
            # somewhat arbitrary.  So we check the last item of parameters to see if it is a weight and,
            # if so, use it.
            try:
                w = _params[-1]
            except IndexError:
                self.params = tuple(_params)
                self.weight = None
            else:
                # A trailing "q" parameter is a weight only if its value is an
                # unquoted, in-range qvalue (0..1). A quoted or out-of-range "q"
                # is an ordinary parameter, not a weight.
                qvalue = as_qvalue(w.value) if w.name == "q" else None
                if qvalue is not None:
                    self.weight = Weight(qvalue=qvalue)
                    self.params = tuple(_params[:-1])
                else:
                    self.params = tuple(_params)
                    self.weight = None

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, self.__class__) and self.__dict__ == __o.__dict__

    def __hash__(self) -> int:
        return hash((self.type, self.subtype, self.params, self.weight))

    def __str__(self):
        return (
            f"{self.type}/{self.subtype}"
            + ((";" + ";".join(str(p) for p in self.params)) if self.params else "")
            + (";" + str(self.weight) if self.weight else "")
        )


class AcceptVisitor(NodeVisitor):
    visit_media_range = MediaRangeVisitor()
    visit_weight = WeightVisitor()

    def visit_accept(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        accept_types = [
            AcceptType(
                media_range.type,
                media_range.subtype,
                params=media_range.params,
                weight=weight,
            )
            for media_range, weight in base.transform(items, MediaRange, Weight)
        ]
        return accept_types
