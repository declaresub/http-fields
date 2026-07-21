import re
from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["Weight", "WeightVisitor", "as_qvalue"]

# qvalue = ( "0" [ "." 0*3DIGIT ] ) / ( "1" [ "." 0*3("0") ] ) -- unquoted, 0..1.
_QVALUE_RE = re.compile(r"^(?:0(?:\.\d{0,3})?|1(?:\.0{0,3})?)$")


def as_qvalue(value: object) -> float | None:
    """Return the float weight if ``value`` is a syntactically valid, unquoted
    qvalue in [0, 1]; otherwise None (so a quoted or out-of-range "q" stays an
    ordinary parameter rather than crashing or being silently clamped)."""
    text = str(value)
    return float(text) if _QVALUE_RE.match(text) else None


@dataclass(frozen=True)
class Weight:
    qvalue: float

    def __str__(self):
        return f"q={self.qvalue:.3f}".rstrip("0").rstrip(".")


class WeightVisitor(NodeVisitor):
    def visit_weight(self, node: Node) -> Weight:
        # We ignore everything other than the qvalue. Filter on "is not None"
        # rather than truthiness: a qvalue of 0.0 is valid ("not acceptable")
        # but falsy, so filter(None, ...) would wrongly discard it.
        qvalue: float = next(
            value for value in map(self.visit, node.children) if value is not None
        )
        return Weight(qvalue=qvalue)

    @staticmethod
    def visit_qvalue(node: Node):
        return float(node.value)
