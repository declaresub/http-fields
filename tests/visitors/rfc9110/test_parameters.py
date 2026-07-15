from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.parameters import (
    Parameter,
    ParametersVisitor,
    ParameterVisitor,
)
from http_headers.visitors.rfc9110.quotedstring import QuotedString
from http_headers.visitors.rfc9110.token import Token


def test_parameter():
    p = Parameter("foo", "bar")
    assert p.name == Token("foo")
    assert p.value == Token("bar")


def test_parameter_qs_value():
    p = Parameter("foo", "bar baz")
    assert p.name == Token("foo")
    assert p.value == QuotedString("bar baz")


def test_parameter_eq():
    assert Parameter("foo", "bar") == Parameter("foo", "bar")


def test_parameter_class_mismatch():
    assert Parameter("foo", "bar") != "foo=bar"


def test_parameter_str():
    assert str(Parameter("foo", "bar")) == "foo=bar"


def test_parameter_visitor():
    src = "foo=bar"
    node = rfc9110.Rule("parameter").parse_all(src)
    visitor = ParameterVisitor()
    param = visitor.visit(node)
    assert param.name == Token("foo")
    assert param.value == Token("bar")


def test_parameters_visitor():
    src = ";foo=bar"
    node = rfc9110.Rule("parameters").parse_all(src)
    visitor = ParametersVisitor()
    params = visitor.visit(node)
    assert params == [Parameter("foo", "bar")]
