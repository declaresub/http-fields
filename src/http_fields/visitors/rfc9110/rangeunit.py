from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

import http_fields.visitors.rfc9110.token as token
from http_fields.parsedobjs import CaselessMixin, ParsedStr


class RangeUnit(CaselessMixin, ParsedStr):
    parser = rfc9110.Rule("range-unit")


class RangeUnitVisitor(NodeVisitor):
    visit_token = token.TokenVisitor()

    def visit_range_unit(self, node: Node):
        item = next(filter(None, map(self.visit, node.children)))
        return RangeUnit(item, parse=False)
