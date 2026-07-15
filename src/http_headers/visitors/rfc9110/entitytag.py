from abnf import Node, NodeVisitor, ParseError
from abnf.grammars import rfc9110


class EntityTag:
    def __init__(self, tag: str, weak: bool = False):
        # check to see if s double-quoted. If not, do so before validating.
        opaque_tag = (
            f'"{tag}"' if not tag or (tag[0] != '"' and tag[-1] != '"') else tag
        )
        entity_tag = f"W/{opaque_tag}" if weak else opaque_tag
        try:
            rfc9110.Rule("entity-tag").parse_all(entity_tag)
        except ParseError as exc:
            raise ValueError("Invalid character in value.") from exc
        self.opaque_tag = opaque_tag
        self.weak = weak

    def __str__(self) -> str:
        return f"W/{self.opaque_tag}" if self.weak else self.opaque_tag

    def __eq__(self, __o: object) -> bool:
        # beware that etag comparison is not this.
        return (
            self.weak == __o.weak and self.opaque_tag == __o.opaque_tag
            if isinstance(__o, self.__class__)
            else NotImplemented
        )

    def __hash__(self) -> int:
        return hash((self.weak, self.opaque_tag))

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
        items = list(filter(None, map(self.visit, node.children)))
        weak, tag = items if len(items) == 2 else (False, items[0])
        return EntityTag(tag, weak=weak)

    def visit_opaque_tag(self, node: Node) -> str:
        return "".join(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_weak(node: Node):
        return node.value != ""

    @staticmethod
    def visit_etagc(node: Node) -> str:
        return node.value
