from dataclasses import dataclass

from abnf import Node, NodeVisitor

from http_headers.visitors.rfc9110.parameters import Parameter
from http_headers.visitors.rfc9110.quotedstring import QuotedStringVisitor
from http_headers.visitors.rfc9110.token import Token, TokenVisitor
from http_headers.visitors.rfc9110.weight import Weight, WeightVisitor, as_qvalue

__all__ = ["TCoding", "TEVisitor"]


@dataclass(frozen=True)
class TCoding:
    """A single TE t-coding: a transfer-coding (or "trailers") with an optional weight and
    transfer-parameters."""

    coding: Token
    weight: Weight | None = None
    parameters: tuple[Parameter, ...] = ()

    def __init__(
        self,
        coding: str,
        weight: Weight | None = None,
        parameters: tuple[Parameter, ...] = (),
    ) -> None:
        # coding self-validates as a Token; weight and Parameter are already safe.
        object.__setattr__(self, "coding", Token(coding))
        object.__setattr__(self, "weight", weight)
        object.__setattr__(self, "parameters", tuple(parameters))

    def __str__(self) -> str:
        parts = [self.coding, *(str(p) for p in self.parameters)]
        if self.weight is not None:
            parts.append(str(self.weight))
        return ";".join(parts)


class TEVisitor(NodeVisitor):
    visit_token = TokenVisitor()
    visit_quoted_string = QuotedStringVisitor()
    visit_weight = WeightVisitor()

    def visit_transfer_parameter(self, node: Node) -> Parameter:
        items = [x for x in map(self.visit, node.children) if x is not None]
        return Parameter(str(items[0]), str(items[-1]))

    def visit_transfer_coding(self, node: Node) -> tuple[Token, list[Parameter]]:
        coding: Token | None = None
        params: list[Parameter] = []
        for child in node.children:
            result = self.visit(child)
            if isinstance(result, Parameter):
                params.append(result)
            elif isinstance(result, Token):
                coding = result
        assert coding is not None
        return (coding, params)

    def visit_t_codings(self, node: Node) -> TCoding:
        if node.value.strip().lower() == "trailers":
            return TCoding("trailers")
        coding = ""
        weight: Weight | None = None
        params: list[Parameter] = []
        for child in node.children:
            result = self.visit(child)
            if isinstance(result, tuple):
                coding, params = result
            elif isinstance(result, Weight):
                weight = result
        # the parser usually captures "q=..." as a transfer-parameter rather than a weight.
        # Only treat it as a weight if it is an unquoted, in-range qvalue.
        if weight is None and params and str(params[-1].name).lower() == "q":
            qvalue = as_qvalue(params[-1].value)
            if qvalue is not None:
                weight = Weight(qvalue=qvalue)
                params = params[:-1]
        return TCoding(coding, weight, tuple(params))

    def visit_te(self, node: Node) -> list[TCoding]:
        return [x for x in map(self.visit, node.children) if isinstance(x, TCoding)]
