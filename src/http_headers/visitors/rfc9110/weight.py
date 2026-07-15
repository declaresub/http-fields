from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["Weight", "WeightVisitor"]


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
