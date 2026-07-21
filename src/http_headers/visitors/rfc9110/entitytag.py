from dataclasses import dataclass

from abnf import Node, NodeVisitor, ParseError
from abnf.grammars import rfc9110


@dataclass(frozen=True)
class EntityTag:
    """An RFC 9110 entity-tag. ``__eq__``/``__hash__`` are exact (weak flag + opaque
    tag); use :meth:`compare` for the RFC's weak/strong comparison semantics."""

    opaque_tag: str
    weak: bool = False

    def __init__(self, tag: str, weak: bool = False) -> None:
        # Double-quote the tag if it is not already, then validate.
        opaque_tag = (
            f'"{tag}"' if not tag or (tag[0] != '"' and tag[-1] != '"') else tag
        )
        entity_tag = f"W/{opaque_tag}" if weak else opaque_tag
        try:
            rfc9110.Rule("entity-tag").parse_all(entity_tag)
        except ParseError as exc:
            raise ValueError("Invalid character in value.") from exc
        object.__setattr__(self, "opaque_tag", opaque_tag)
        object.__setattr__(self, "weak", weak)

    def __str__(self) -> str:
        return f"W/{self.opaque_tag}" if self.weak else self.opaque_tag

    def compare(self, __o: object, *, weak: bool) -> bool:
        if not isinstance(__o, self.__class__):
            raise TypeError(
                f"EntityTag is not comparable to an instance of {__o.__class__.__name__}."
            )

        if weak:
            return self.opaque_tag == __o.opaque_tag
        else:
            return not (self.weak or __o.weak) and self.opaque_tag == __o.opaque_tag


class EntityTagVisitor(NodeVisitor):
    def visit_entity_tag(self, node: Node) -> EntityTag:
        # Match children by name: an empty opaque-tag ("") and an absent weak
        # flag are both falsy, so a truthiness filter would lose them and shift
        # the positional unpacking.
        weak = False
        tag = ""
        for child in node.children:
            if child.name == "weak":
                weak = self.visit(child)
            elif child.name == "opaque-tag":
                tag = self.visit(child)
        return EntityTag(tag, weak=weak)

    def visit_opaque_tag(self, node: Node) -> str:
        return "".join(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_weak(node: Node):
        return node.value != ""

    @staticmethod
    def visit_etagc(node: Node) -> str:
        return node.value
