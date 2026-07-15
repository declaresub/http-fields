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


@dataclass(frozen=True)
class WeightedLanguageRange:
    language_range: LanguageRange
    weight: Weight | None

    def __init__(self, language_range: str, weight: float | Weight | None = None):
        object.__setattr__(self, "language_range", LanguageRange(language_range))
        if isinstance(weight, Weight):
            object.__setattr__(self, "weight", weight)
        elif isinstance(weight, (int, float)) and not isinstance(weight, bool):
            # a numeric 0 is a valid weight ("not acceptable"); only None means unset.
            object.__setattr__(self, "weight", Weight(float(weight)))
        else:
            object.__setattr__(self, "weight", None)

    def __str__(self) -> str:
        return str(self.language_range) + (f";{self.weight}" if self.weight else "")


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
