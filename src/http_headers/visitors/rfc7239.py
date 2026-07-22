from dataclasses import dataclass

from abnf import Node, NodeVisitor

from http_headers.visitors.rfc9110.parameters import (
    Param,
    ParamsInput,
    as_params,
    parsed_param,
)

__all__ = ["ForwardedElement", "ForwardedVisitor"]


@dataclass(frozen=True)
class ForwardedElement:
    """One Forwarded element (RFC 7239): an ordered sequence of ``name=value`` pairs,
    e.g. ``for=192.0.2.60;proto=http``."""

    pairs: tuple[Param, ...]

    def __init__(self, pairs: ParamsInput) -> None:
        # Each pair is a self-validating Param; raw (name, value) tuples are coerced.
        object.__setattr__(self, "pairs", as_params(pairs))

    def __str__(self) -> str:
        return ";".join(str(p) for p in self.pairs)


class ForwardedVisitor(NodeVisitor):
    @staticmethod
    def visit_forwarded_pair(node: Node) -> Param:
        # forwarded-pair = token "=" value
        return parsed_param(node.children[0].value, node.children[-1].value)

    def visit_forwarded_element(self, node: Node) -> ForwardedElement:
        pairs = [x for x in map(self.visit, node.children) if isinstance(x, Param)]
        return ForwardedElement(pairs)

    def visit_forwarded(self, node: Node) -> list[ForwardedElement]:
        return [
            x for x in map(self.visit, node.children) if isinstance(x, ForwardedElement)
        ]
