from typing import Any

import pytest
from abnf.grammars import rfc6266

from http_fields.visitors.rfc6266 import (
    ContentDispositionNodeVisitor,
    DispExtParm,
    DispExtParmVisitor,
    DispositionParmNodeVisitor,
    DispositionType,
    DispositionTypeVisitor,
    ExtValue,
    ExtValueVisitor,
    Filename,
    FilenameParm,
    FilenameParmNodeVisitor,
    NotNone,
    ValueVisitor,
)
from http_fields.visitors.rfc7230 import QuotedString, Token


def test_dispositiontypevisitor():
    src = "inline"
    node = rfc6266.Rule("disposition-type").parse_all(src)
    visitor = DispositionTypeVisitor()
    assert visitor.visit(node) == DispositionType("inline")


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, False),
        ("test", True),
    ],
)
def test_notnone(value: Any, expected: bool):
    assert NotNone(value) == expected


def test_ext_value_str():
    value = ExtValue(value="mooƒ.txt")
    assert str(value) == "utf-8''moo%C6%92.txt"


def test_ext_value_visitor():
    src = "utf-8'en-US'moo%C6%92.txt"
    node = rfc6266.Rule("ext-value").parse_all(src)
    value = ExtValueVisitor().visit(node)
    assert value == ExtValue(charset="utf-8", language="en-US", value="mooƒ.txt")


def test_filename_from_filename():
    name = Filename("filename")
    assert Filename(name) is name


def test_filename_bad_value():
    with pytest.raises(ValueError):
        Filename("fail")


def test_filename_repr():
    name = Filename("filename")
    assert repr(name) == "Filename('filename')"


def test_filename_parm_bad_value():
    with pytest.raises(ValueError):
        FilenameParm("filename", "\n")


@pytest.mark.parametrize(
    "src, expected",
    [
        ("token", Token("token")),
        ('"quoted string"', QuotedString('"quoted string"')),
    ],
)
def test_value_visitor(src: str, expected: Token | QuotedString):
    node = rfc6266.Rule("value").parse_all(src)
    assert ValueVisitor().visit(node) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            FilenameParm("filename", "test.txt"),
            FilenameParm("filename", Token("test.txt")),
        ),
        (
            FilenameParm("filename", "another test.txt"),
            FilenameParm("filename", QuotedString("another test.txt")),
        ),
        (
            FilenameParm("filename*", "mooƒ.txt"),
            FilenameParm("filename*", ExtValue(value="mooƒ.txt")),
        ),
    ],
)
def test_filenameparm(value: FilenameParm, expected: FilenameParm):
    assert value == expected


def test_filenameparm_bad_args():
    with pytest.raises(TypeError):
        FilenameParm("filename", ExtValue(value="oops"))


def test_filenameparm_str():
    assert str(FilenameParm("filename", "test.html")) == "filename=test.html"


@pytest.mark.parametrize(
    "src, expected",
    [
        ("filename=test.txt", FilenameParm("filename", Token("test.txt"))),
        (
            "filename*=utf-8'en-US'moo%C6%92.txt",
            FilenameParm(
                "filename*",
                ExtValue(charset="utf-8", language="en-US", value="mooƒ.txt"),
            ),
        ),
    ],
)
def test_filenameparmvisitor(src: str, expected: FilenameParm):
    node = rfc6266.Rule("filename-parm").parse_all(src)
    assert FilenameParmNodeVisitor().visit(node) == expected


@pytest.mark.parametrize(
    "args, expected",
    [
        (("foo*", "bar"), DispExtParm("foo*", "bar")),
        (("foo*", ExtValue(value="bar")), DispExtParm("foo*", "bar")),
        (("foo", "bar"), DispExtParm("foo", "bar")),
        (("foo", '"bar baz"'), DispExtParm("foo", QuotedString("bar baz"))),
    ],
)
def test_dispextparm(args: tuple[str, str], expected: DispExtParm):
    assert DispExtParm(*args) == expected


def test_dispextparm_bad_value():
    with pytest.raises(ValueError):
        DispExtParm("foo", "bar\nbaz")


def test_dispextparm_bad_type():
    with pytest.raises(TypeError):
        DispExtParm("foo", ExtValue(value="bar"))


@pytest.mark.parametrize(
    "src, expected",
    [
        ("foo=bar", DispExtParm("foo", "bar")),
        (
            "test*=utf-8'en-US'moo%C6%92.txt",
            DispExtParm(
                "test*", ExtValue(charset="utf-8", language="en-US", value="mooƒ.txt")
            ),
        ),
    ],
)
def test_dispextparm_visitor(src: str, expected: DispExtParm):
    node = rfc6266.Rule("disp-ext-parm").parse_all(src)
    parm = DispExtParmVisitor().visit(node)
    assert parm == expected


@pytest.mark.parametrize(
    "src, expected",
    [
        ("filename=test.txt", FilenameParm("filename", Token("test.txt"))),
        ("foo=bar", DispExtParm("foo", "bar")),
    ],
)
def test_dispositionparm_visitor(src: str, expected: FilenameParm | DispExtParm):
    node = rfc6266.Rule("disposition-parm").parse_all(src)
    assert DispositionParmNodeVisitor().visit(node) == expected


@pytest.mark.parametrize(
    "src, expected",
    [
        (
            "content-disposition: attachment; filename=example.html",
            (
                DispositionType("attachment"),
                [FilenameParm("filename", Token("example.html"))],
            ),
        ),
    ],
)
def test_contentdispositionvisitor(
    src: str, expected: tuple[DispositionType, list[FilenameParm | DispExtParm]]
):
    node = rfc6266.Rule("content-disposition").parse_all(src)
    assert ContentDispositionNodeVisitor().visit(node) == expected
