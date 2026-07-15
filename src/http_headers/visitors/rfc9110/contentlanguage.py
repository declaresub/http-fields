from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_headers.parsedobjs import CaselessMixin, ParsedStr

__all__ = ["ContentLanguageVisitor", "LanguageTag"]


class LanguageTag(CaselessMixin, ParsedStr):
    """Represents an RFC 9110 language-tag (BCP 47), matched case-insensitively."""

    parser = rfc9110.Rule("language-tag")


class ContentLanguageVisitor(NodeVisitor):
    @staticmethod
    def visit_language_tag(node: Node) -> str:
        return LanguageTag(node.value, parse=False)

    def visit_content_language(self, node: Node) -> list[str]:
        return [x for x in map(self.visit, node.children) if x is not None]
