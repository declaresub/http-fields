from __future__ import annotations

from dataclasses import dataclass

from abnf import Node, NodeVisitor, ParseError
from abnf.grammars import rfc9110

import http_fields.visitors.rfc9110.quotedstring as quotedstring


def _escape_ctext(text: str) -> str:
    # ctext excludes "(", ")" and "\"; these appear in parsed text only because a
    # quoted-pair was unescaped, so re-escape them to keep the comment parseable.
    return "".join("\\" + c if c in "()\\" else c for c in text)


@dataclass(frozen=True)
class Comment:
    """An RFC 9110 comment: a parenthesised sequence of text runs and nested comments.

    Frozen so it stays immutable (and stably hashable) while embedded in a frozen
    User-Agent/Server/Via header. ``__eq__``/``__hash__``/``__repr__`` are generated;
    ``__str__`` re-escapes text runs so the serialized comment round-trips.

    Each string argument is parsed as comment *content* (``*( ctext / quoted-pair /
    comment )``): embedded ``(...)`` become nested Comment objects, ``\\)`` is a
    quoted-pair, and invalid content (CR/LF/NUL or an unescaped/unbalanced parenthesis)
    raises ``ValueError``. So ``Comment(s)`` accepts exactly what the parser produces.
    """

    items: tuple[str | Comment, ...] = ()

    def __init__(self, *items: str | Comment) -> None:
        parsed: list[str | Comment] = []
        for item in items:
            if isinstance(item, Comment):
                parsed.append(item)
            else:
                parsed.extend(_parse_content(item))
        object.__setattr__(self, "items", tuple(parsed))

    @classmethod
    def _from_items(cls, items: tuple[str | Comment, ...]) -> Comment:
        # Build from already-structured, already-unescaped items (the visitor's
        # output), bypassing the string-parsing done by __init__.
        obj = object.__new__(cls)
        object.__setattr__(obj, "items", items)
        return obj

    def __str__(self) -> str:
        return (
            "("
            + "".join(
                str(item) if isinstance(item, Comment) else _escape_ctext(str(item))
                for item in self.items
            )
            + ")"
        )


def _parse_content(content: str) -> tuple[str | Comment, ...]:
    """Parse a comment-content string into its (text-run / nested-Comment) items."""
    try:
        node = rfc9110.Rule("comment").parse_all(f"({content})")
    except ParseError as exc:
        raise ValueError(f"Invalid comment content: {content!r}.") from exc
    return _CONTENT_VISITOR.visit(node).items


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
        # Build directly from the (already-unescaped) items; passing them back
        # through Comment.__init__ would try to re-parse them as content. This is the
        # module's own internal factory (same file), not cross-module private access.
        return Comment._from_items(tuple(comment_items))  # pyright: ignore[reportPrivateUsage]


_CONTENT_VISITOR = CommentVisitor()
