from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.comment import Comment, CommentVisitor


def test_comment():
    comment = Comment("this is a ", Comment("test"))
    assert str(comment) == "(this is a (test))"


def test_comment_hash():
    assert isinstance(hash(Comment("test")), int)


def test_comment_visitor():
    src = "(this \\(is\\) a (test))"
    node = rfc9110.Rule("comment").parse_all(src)
    visitor = CommentVisitor()
    assert visitor.visit(node) == Comment("this (is) a ", Comment("test"))
