from __future__ import annotations

from abnf import Node, NodeVisitor

import http_headers.visitors.rfc9110.quotedstring as quotedstring


def _escape_ctext(text: str) -> str:
    # ctext excludes "(", ")" and "\"; these appear in parsed text only because a
    # quoted-pair was unescaped, so re-escape them to keep the comment parseable.
    return "".join("\\" + c if c in "()\\" else c for c in text)


class Comment:
    def __init__(self, *items: str | Comment):
        # A tuple keeps the value immutable, so the hash stays stable while a
        # Comment is used as a dict key or in a set (e.g. inside a frozen
        # UserAgent/Server/Via).
        self.items = tuple(items)

    def __str__(self):
        return (
            "("
            + "".join(
                str(item) if isinstance(item, Comment) else _escape_ctext(str(item))
                for item in self.items
            )
            + ")"
        )

    def __eq__(self, __o: object) -> bool:
        return (
            self.items == __o.items
            if isinstance(__o, self.__class__)
            else NotImplemented
        )

    def __hash__(self) -> int:
        return hash(tuple(self.items))


class CommentVisitor(NodeVisitor):
    visit_quoted_pair = quotedstring.QuotedPairVisitor()

    @staticmethod
    def visit_ctext(node: Node):
        return node.value

    def visit_comment(self, node: Node):
        items = filter(None, map(self.visit, node.children))
        comment_items: list[str | Comment] = []

        text: list[str] = []
        for item in items:
            if isinstance(item, str):
                text.append(item)
            elif isinstance(item, Comment):
                comment_items.append("".join(text))
                text = []
                comment_items.append(item)
            else:  # pragma: no cover
                raise AssertionError()
        if text:
            comment_items.append("".join(text))
        return Comment(*comment_items)
