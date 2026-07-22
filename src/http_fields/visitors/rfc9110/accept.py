from __future__ import annotations

from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110._base as base
import http_fields.visitors.rfc9110.parameters as parameters
import http_fields.visitors.rfc9110.token as token
import http_fields.visitors.rfc9110.type as type_grammar
import http_fields.visitors.rfc9110.weight as weight

# NB: do not alias the "type" grammar module as `type` -- it would shadow the
# builtin, which a frozen dataclass's generated __setattr__ (`type(self)`) needs.
Parameter = parameters.Parameter
ParametersVisitor = parameters.ParametersVisitor
SubtypeVisitor = type_grammar.SubtypeVisitor
Token = token.Token
TypeVisitor = type_grammar.TypeVisitor
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


@dataclass(frozen=True)
class AcceptType:
    type: Token
    subtype: Token
    params: tuple[Parameter, ...] = ()
    weight: Weight | None = None

    def __init__(
        self,
        type: str,
        subtype: str,
        *,
        params: list[tuple[str, str] | Parameter] | None = None,
        weight: float | Weight | None = None,
    ) -> None:
        _params = (
            [Parameter(*p) if isinstance(p, tuple) else p for p in params]
            if params
            else []
        )
        resolved_weight: Weight | None
        if isinstance(weight, (float, Weight)):
            resolved_weight = (
                Weight(qvalue=weight) if isinstance(weight, float) else weight
            )
            resolved_params = tuple(_params)
        elif _params:
            # sometimes, weight was captured by parser as a parameter because abnf
            # backtracking is somewhat arbitrary. A trailing "q" parameter is a weight
            # only if its value is an unquoted, in-range qvalue (0..1); a quoted or
            # out-of-range "q" is an ordinary parameter.
            w = _params[-1]
            qvalue = as_qvalue(w.value) if w.name == "q" else None
            if qvalue is not None:
                resolved_weight = Weight(qvalue=qvalue)
                resolved_params = tuple(_params[:-1])
            else:
                resolved_weight = None
                resolved_params = tuple(_params)
        else:
            resolved_weight = None
            resolved_params = tuple(_params)
        object.__setattr__(self, "type", Token(type))
        object.__setattr__(self, "subtype", Token(subtype))
        object.__setattr__(self, "params", resolved_params)
        object.__setattr__(self, "weight", resolved_weight)

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
