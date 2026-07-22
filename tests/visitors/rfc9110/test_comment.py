from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.comment import Comment, CommentVisitor


def test_comment():
    comment = Comment("this is a ", Comment("test"))
    assert str(comment) == "(this is a (test))"


def test_comment_hash():
    assert isinstance(hash(Comment("test")), int)


def test_comment_visitor():
    src = "(this \\(is\\) a (test))"
    node = rfc9110.Rule("comment").parse_all(src)
    visitor = CommentVisitor()
    # A literal "(" / ")" in a text run must be written escaped when constructing
    # from a string, since Comment(str) parses its argument as comment content.
    assert visitor.visit(node) == Comment(r"this \(is\) a ", Comment("test"))
