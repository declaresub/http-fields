from dataclasses import dataclass

from abnf import Node, NodeVisitor

from http_headers.visitors.rfc9110.parameters import Parameter
from http_headers.visitors.rfc9110.quotedstring import QuotedStringVisitor
from http_headers.visitors.rfc9110.token import Token, TokenVisitor
from http_headers.visitors.rfc9110.weight import Weight, WeightVisitor

__all__ = ["TCoding", "TEVisitor"]


@dataclass(frozen=True)
class TCoding:
    """A single TE t-coding: a transfer-coding (or "trailers") with an optional weight and
    transfer-parameters."""

    coding: str
    weight: Weight | None = None
    parameters: tuple[Parameter, ...] = ()

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

    def visit_transfer_coding(self, node: Node) -> tuple[str, list[Parameter]]:
        coding = ""
        params: list[Parameter] = []
        for child in node.children:
            result = self.visit(child)
            if isinstance(result, Parameter):
                params.append(result)
            elif isinstance(result, Token):
                coding = str(result)
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
        if weight is None and params and str(params[-1].name).lower() == "q":
            weight = Weight(qvalue=max(min(float(params[-1].value), 1.0), 0.0))
            params = params[:-1]
        return TCoding(coding, weight, tuple(params))

    def visit_te(self, node: Node) -> list[TCoding]:
        return [x for x in map(self.visit, node.children) if isinstance(x, TCoding)]
