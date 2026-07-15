from dataclasses import dataclass

from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

import http_headers.visitors.rfc9110._base as base
import http_headers.visitors.rfc9110.token as token
import http_headers.visitors.rfc9110.weight as weight
from http_headers.parsedobjs import ParsedStr

__all__ = ["WeightedLanguageRange", "AcceptLanguageVisitor"]

Token = token.Token
Weight = weight.Weight
WeightVisitor = weight.WeightVisitor


class LanguageRange(ParsedStr):
    """Represents an RFC 9110 language-range."""

    parser = rfc9110.Rule("language-range")


@dataclass
class WeightedLanguageRange:
    language_range: LanguageRange
    weight: Weight | None

    def __init__(self, language_range: str, weight: float | Weight | None = None):
        self.language_range = LanguageRange(language_range)
        self.weight = (
            weight
            if isinstance(weight, Weight)
            else Weight(weight)
            if isinstance(weight, float)
            else None
        )


class AcceptLanguageVisitor(NodeVisitor):
    visit_weight = WeightVisitor()

    @staticmethod
    def visit_language_range(node: Node):
        return LanguageRange(node.value)

    def visit_accept_language(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        return [
            WeightedLanguageRange(enc, weight)
            for enc, weight in base.transform(items, LanguageRange, weight.Weight)
        ]
