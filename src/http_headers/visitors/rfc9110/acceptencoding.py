from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from abnf import Node
from abnf import NodeVisitor as _NodeVisitor
from abnf.grammars import rfc9110

import http_headers.visitors.rfc9110._base as base
import http_headers.visitors.rfc9110.token as token
import http_headers.visitors.rfc9110.weight as weight
from http_headers.parsedobjs import ParsedStr

Token = token.Token
TokenVisitor = token.TokenVisitor
Weight = weight.Weight
WeightVisitor = weight.WeightVisitor


class NodeVisitor(_NodeVisitor):
    def visit_children(self, node: Node, *, f: Callable[[Any], bool] | None = None):
        for child in node.children:
            result = self.visit(child)
            if (f and f(result)) or result is not None:
                yield result


class Coding(ParsedStr):
    """Represents an RFC 9110 codings thing."""

    parser = rfc9110.Rule("codings")


@dataclass
class WeightedCoding:
    coding: Coding
    weight: Weight | None

    def __init__(self, coding: str, weight: float | (Weight | None) = None):
        self.coding = Coding(coding)
        if isinstance(weight, Weight):
            self.weight = weight
        elif isinstance(weight, (int, float)) and not isinstance(weight, bool):
            # Accept any real number, including 0 ("not acceptable"); a bare
            # None means no weight was specified.
            self.weight = Weight(float(weight))
        else:
            self.weight = None

    def __str__(self):
        return str(self.coding) + (f";{str(self.weight)}" if self.weight else "")


class AcceptEncodingVisitor(NodeVisitor):
    visit_weight = WeightVisitor()
    visit_token = TokenVisitor()

    @staticmethod
    def visit_literal(node: Node):
        return node.value if node.value in {"identity", "*"} else None

    def visit_content_coding(self, node: Node):
        item: Token = next(filter(None, map(self.visit, node.children)))
        return Coding(item)

    def visit_codings(self, node: Node):
        item: Coding = next(filter(None, map(self.visit, node.children)))
        return item

    def visit_accept_encoding(self, node: Node):
        # items = filter(None, map(self.visit, node.children))
        items = self.visit_children(node)
        return [
            WeightedCoding(enc, weight)
            for enc, weight in base.transform(items, Coding, Weight)
        ]
